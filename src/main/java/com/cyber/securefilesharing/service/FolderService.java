package com.cyber.securefilesharing.service;

import com.cyber.securefilesharing.model.Folder;
import com.cyber.securefilesharing.model.FolderTemplate;
import com.cyber.securefilesharing.model.UserAccount;
import com.cyber.securefilesharing.repository.FolderRepository;
import com.cyber.securefilesharing.repository.FolderTemplateRepository;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class FolderService {

    private final FolderRepository folderRepository;
    private final FolderTemplateRepository templateRepository;

    public FolderService(FolderRepository folderRepository, FolderTemplateRepository templateRepository) {
        this.folderRepository = folderRepository;
        this.templateRepository = templateRepository;
    }

    public List<Folder> getRootFolders(UserAccount owner) {
        return folderRepository.findByOwnerAndParentIsNull(owner);
    }

    public List<Folder> getSubfolders(UserAccount owner, Long parentId) {
        Folder parent = folderRepository.findById(parentId)
            .orElseThrow(() -> new RuntimeException("Folder not found"));
        return folderRepository.findByOwnerAndParent(owner, parent);
    }

    @Transactional
    public Folder createFolder(String name, UserAccount owner, Long parentId) {
        Folder folder = new Folder();
        folder.setName(name);
        folder.setOwner(owner);
        if (parentId != null) {
            Folder parent = folderRepository.findById(parentId)
                .orElseThrow(() -> new RuntimeException("Parent folder not found"));
            folder.setParent(parent);
        }
        return folderRepository.save(folder);
    }

    @Transactional
    public void applyTemplate(Long templateId, UserAccount owner) {
        FolderTemplate template = templateRepository.findById(templateId)
            .orElseThrow(() -> new RuntimeException("Template not found"));
        for (String path : template.getFolderPaths()) {
            createPath(path, owner);
        }
    }

    private void createPath(String path, UserAccount owner) {
        String[] parts = path.split("/");
        Folder currentParent = null;
        for (String part : parts) {
            if (part.isEmpty()) continue;
            final String name = part;
            final Folder parent = currentParent;
            Optional<Folder> existing = folderRepository.findByOwnerAndParent(owner, parent)
                .stream()
                .filter(f -> f.getName().equals(name))
                .findFirst();

            if (existing.isPresent()) {
                currentParent = existing.get();
            } else {
                Folder newFolder = new Folder();
                newFolder.setName(name);
                newFolder.setOwner(owner);
                newFolder.setParent(parent);
                currentParent = folderRepository.save(newFolder);
            }
        }
    }

    public List<FolderTemplate> getAllTemplates() {
        return templateRepository.findAll();
    }

    @Transactional
    public FolderTemplate createTemplate(String name, List<String> paths) {
        FolderTemplate template = new FolderTemplate();
        template.setName(name);
        template.setFolderPaths(paths);
        return templateRepository.save(template);
    }
}
