package com.cyber.securefilesharing.controller;

import com.cyber.securefilesharing.model.ShareToken;
import com.cyber.securefilesharing.repository.ShareTokenRepository;
import com.cyber.securefilesharing.service.FileStorageService;
import java.time.Instant;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/share")
public class ShareController {

    private final ShareTokenRepository shareTokenRepository;
    private final FileStorageService fileStorageService;

    public ShareController(ShareTokenRepository shareTokenRepository, FileStorageService fileStorageService) {
        this.shareTokenRepository = shareTokenRepository;
        this.fileStorageService = fileStorageService;
    }

    @GetMapping("/{token}")
    public ResponseEntity<Resource> downloadSharedFile(@PathVariable String token) {
        ShareToken shareToken = shareTokenRepository.findByToken(token)
            .filter(entry -> entry.getExpiresAt().isAfter(Instant.now()))
            .orElseThrow(() -> new IllegalArgumentException("Share token expired or invalid"));

        Resource resource = fileStorageService.loadAsResource(shareToken.getFileMetadata().getStorageName());
        String filename = shareToken.getFileMetadata().getFileName();
        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
            .body(resource);
    }
}
