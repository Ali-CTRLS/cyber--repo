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

    public static class FileInfo {
        private Long id;
        private String fileName;
        private long size;
        private Instant uploadedAt;
        public FileInfo(Long id, String fileName, long size, Instant uploadedAt) {
            this.id = id; this.fileName = fileName; this.size = size; this.uploadedAt = uploadedAt;
        }
        public Long getId() { return id; }
        public String getFileName() { return fileName; }
        public long getSize() { return size; }
        public Instant getUploadedAt() { return uploadedAt; }
    }
    
    public static class ShareRequest {
        private Long fileId;
        private Integer expiresMinutes;
        public Long getFileId() { return fileId; }
        public void setFileId(Long fileId) { this.fileId = fileId; }
        public Integer getExpiresMinutes() { return expiresMinutes; }
        public void setExpiresMinutes(Integer expiresMinutes) { this.expiresMinutes = expiresMinutes; }
    }
    
    public static class ShareResponse {
        private String shareUrl;
        private Instant expiresAt;
        public ShareResponse(String shareUrl, Instant expiresAt) {
            this.shareUrl = shareUrl; this.expiresAt = expiresAt;
        }
        public String getShareUrl() { return shareUrl; }
        public Instant getExpiresAt() { return expiresAt; }
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> upload(Principal principal, 
                                   @RequestPart("file") MultipartFile file,
                                   @RequestParam(required = false) Long folderId) {
        UserAccount owner = getUser(principal);
        FileMetadata metadata = storageService.storeFile(file, owner, folderId);
        java.util.Map<String, Object> response = new java.util.HashMap<>();
        response.put("id", metadata.getId());
        response.put("fileName", metadata.getFileName());
        return ResponseEntity.created(URI.create("/api/files/" + metadata.getId())).body(response);
    }

    @GetMapping
    public List<FileInfo> listFiles(Principal principal, @RequestParam(required = false) Long folderId) {
        UserAccount owner = getUser(principal);
        return storageService.getFilesForUser(owner, folderId).stream()
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
        FileMetadata metadata = storageService.findById(request.getFileId())
            .filter(file -> file.getOwner().getId().equals(owner.getId()))
            .orElseThrow(() -> new IllegalArgumentException("File not found or access denied"));

        ShareToken token = new ShareToken();
        token.setToken(UUID.randomUUID().toString());
        token.setFileMetadata(metadata);
        token.setExpiresAt(Instant.now().plusSeconds((request.getExpiresMinutes() == null ? 60 : request.getExpiresMinutes()) * 60L));
        shareTokenRepository.save(token);

        String shareUrl = "/share/" + token.getToken();
        return ResponseEntity.ok(new ShareResponse(shareUrl, token.getExpiresAt()));
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(Principal principal) {
        UserAccount owner = getUser(principal);
        java.util.Map<String, Object> response = new java.util.HashMap<>();
        response.put("username", owner.getUsername());
        response.put("id", owner.getId());
        return ResponseEntity.ok(response);
    }

    private UserAccount getUser(Principal principal) {
        return userRepository.findByUsername(principal.getName())
            .orElseThrow(() -> new IllegalArgumentException("Authenticated user not found"));
    }
}
