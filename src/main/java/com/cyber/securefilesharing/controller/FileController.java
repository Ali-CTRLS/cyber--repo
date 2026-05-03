package com.cyber.securefilesharing.controller;

import com.cyber.securefilesharing.model.FileMetadata;
import com.cyber.securefilesharing.model.ShareToken;
import com.cyber.securefilesharing.model.UserAccount;
import com.cyber.securefilesharing.repository.ShareTokenRepository;
import com.cyber.securefilesharing.repository.UserRepository;
import com.cyber.securefilesharing.service.FileStorageService;
import jakarta.servlet.http.HttpServletRequest;
import java.net.URI;
import java.security.Principal;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RequestBody;

@RestController
@RequestMapping("/api/files")
public class FileController {

    private final FileStorageService storageService;
    private final UserRepository userRepository;
    private final ShareTokenRepository shareTokenRepository;

    public FileController(FileStorageService storageService,
                          UserRepository userRepository,
                          ShareTokenRepository shareTokenRepository) {
        this.storageService = storageService;
        this.userRepository = userRepository;
        this.shareTokenRepository = shareTokenRepository;
    }

    record FileInfo(Long id, String fileName, long size, Instant uploadedAt) {}
    record ShareRequest(Long fileId, Integer expiresMinutes) {}
    record ShareResponse(String shareUrl, Instant expiresAt) {}

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> upload(Principal principal, @RequestPart("file") MultipartFile file) {
        UserAccount owner = getUser(principal);
        FileMetadata metadata = storageService.storeFile(file, owner);
        return ResponseEntity.created(URI.create("/api/files/" + metadata.getId()))
                .body(Map.of("id", metadata.getId(), "fileName", metadata.getFileName()));
    }

    @GetMapping
    public List<FileInfo> listFiles(Principal principal) {
        UserAccount owner = getUser(principal);
        return storageService.getFilesForUser(owner).stream()
            .map(file -> new FileInfo(file.getId(), file.getFileName(), file.getSize(), file.getUploadedAt()))
            .collect(Collectors.toList());
    }

    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> download(Principal principal, @PathVariable Long id, HttpServletRequest request) {
        UserAccount owner = getUser(principal);
        FileMetadata metadata = storageService.findById(id)
            .filter(file -> file.getOwner().getId().equals(owner.getId()))
            .orElseThrow(() -> new IllegalArgumentException("File not found or access denied"));

        Resource resource = storageService.loadAsResource(metadata.getStorageName());
        String contentType = Optional.ofNullable(request.getServletContext().getMimeType(resource.getFilename()))
                .orElse(MediaType.APPLICATION_OCTET_STREAM_VALUE);
        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(contentType))
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + metadata.getFileName() + "\"")
            .body(resource);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(Principal principal, @PathVariable Long id) {
        UserAccount owner = getUser(principal);
        FileMetadata metadata = storageService.findById(id)
            .filter(file -> file.getOwner().getId().equals(owner.getId()))
            .orElseThrow(() -> new IllegalArgumentException("File not found or access denied"));
        storageService.deleteFile(metadata);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/share")
    public ResponseEntity<ShareResponse> createShareLink(Principal principal, @RequestBody ShareRequest request) {
        UserAccount owner = getUser(principal);
        FileMetadata metadata = storageService.findById(request.fileId())
            .filter(file -> file.getOwner().getId().equals(owner.getId()))
            .orElseThrow(() -> new IllegalArgumentException("File not found or access denied"));

        ShareToken token = new ShareToken();
        token.setToken(UUID.randomUUID().toString());
        token.setFileMetadata(metadata);
        token.setExpiresAt(Instant.now().plusSeconds((request.expiresMinutes() == null ? 60 : request.expiresMinutes()) * 60L));
        shareTokenRepository.save(token);

        String shareUrl = "/share/" + token.getToken();
        return ResponseEntity.ok(new ShareResponse(shareUrl, token.getExpiresAt()));
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(Principal principal) {
        UserAccount owner = getUser(principal);
        return ResponseEntity.ok(Map.of("username", owner.getUsername(), "id", owner.getId()));
    }

    private UserAccount getUser(Principal principal) {
        return userRepository.findByUsername(principal.getName())
            .orElseThrow(() -> new IllegalArgumentException("Authenticated user not found"));
    }
}
