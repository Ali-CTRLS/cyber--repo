package com.cyber.securefilesharing.service;

import com.cyber.securefilesharing.model.FileMetadata;
import com.cyber.securefilesharing.model.UserAccount;
import com.cyber.securefilesharing.repository.FileMetadataRepository;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class FileStorageService {

    private final Path storageLocation;
    private final FileMetadataRepository repository;

    public FileStorageService(@Value("${storage.location}") String storageLocation, FileMetadataRepository repository) {
        this.storageLocation = Path.of(storageLocation).toAbsolutePath().normalize();
        this.repository = repository;
        try {
            Files.createDirectories(this.storageLocation);
        } catch (IOException e) {
            throw new RuntimeException("Could not create storage directory", e);
        }
    }

    public FileMetadata storeFile(MultipartFile multipartFile, UserAccount owner) {
        try {
            String originalFilename = Path.of(multipartFile.getOriginalFilename()).getFileName().toString();
            String storageName = UUID.randomUUID().toString() + "-" + originalFilename;
            Path target = storageLocation.resolve(storageName);
            Files.copy(multipartFile.getInputStream(), target, StandardCopyOption.REPLACE_EXISTING);

            FileMetadata metadata = new FileMetadata();
            metadata.setFileName(originalFilename);
            metadata.setStorageName(storageName);
            metadata.setSize(multipartFile.getSize());
            metadata.setUploadedAt(Instant.now());
            metadata.setOwner(owner);
            return repository.save(metadata);
        } catch (IOException e) {
            throw new RuntimeException("Failed to store file", e);
        }
    }

    public Resource loadAsResource(String storageName) {
        try {
            Path file = storageLocation.resolve(storageName).normalize();
            Resource resource = new UrlResource(file.toUri());
            if (resource.exists() && resource.isReadable()) {
                return resource;
            }
            throw new RuntimeException("File not found: " + storageName);
        } catch (Exception e) {
            throw new RuntimeException("Could not read file: " + storageName, e);
        }
    }

    public List<FileMetadata> getFilesForUser(UserAccount owner) {
        return repository.findByOwner(owner);
    }

    public Optional<FileMetadata> findById(Long id) {
        return repository.findById(id);
    }

    public void deleteFile(FileMetadata metadata) {
        try {
            Files.deleteIfExists(storageLocation.resolve(metadata.getStorageName()));
            repository.delete(metadata);
        } catch (IOException e) {
            throw new RuntimeException("Could not delete file", e);
        }
    }
}
