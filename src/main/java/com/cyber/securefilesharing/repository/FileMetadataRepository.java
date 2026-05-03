package com.cyber.securefilesharing.repository;

import com.cyber.securefilesharing.model.FileMetadata;
import com.cyber.securefilesharing.model.UserAccount;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FileMetadataRepository extends JpaRepository<FileMetadata, Long> {
    List<FileMetadata> findByOwner(UserAccount owner);
    List<FileMetadata> findByOwnerAndFolderIsNull(UserAccount owner);
    List<FileMetadata> findByOwnerAndFolder(UserAccount owner, com.cyber.securefilesharing.model.Folder folder);
}
