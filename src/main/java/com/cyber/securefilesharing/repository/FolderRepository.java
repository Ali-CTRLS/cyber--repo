package com.cyber.securefilesharing.repository;

import com.cyber.securefilesharing.model.Folder;
import com.cyber.securefilesharing.model.UserAccount;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface FolderRepository extends JpaRepository<Folder, Long> {
    List<Folder> findByOwnerAndParentIsNull(UserAccount owner);
    List<Folder> findByOwnerAndParent(UserAccount owner, Folder parent);
}
