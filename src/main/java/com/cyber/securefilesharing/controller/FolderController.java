package com.cyber.securefilesharing.controller;

import com.cyber.securefilesharing.model.Folder;
import com.cyber.securefilesharing.model.FolderTemplate;
import com.cyber.securefilesharing.model.UserAccount;
import com.cyber.securefilesharing.repository.UserRepository;
import com.cyber.securefilesharing.service.FolderService;
import java.security.Principal;
import java.util.List;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/folders")
public class FolderController {

    private final FolderService folderService;
    private final UserRepository userRepository;

    public FolderController(FolderService folderService, UserRepository userRepository) {
        this.folderService = folderService;
        this.userRepository = userRepository;
    }

    public static class FolderRequest {
        private String name;
        private Long parentId;
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public Long getParentId() { return parentId; }
        public void setParentId(Long parentId) { this.parentId = parentId; }
    }
    
    public static class TemplateRequest {
        private String name;
        private List<String> paths;
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public List<String> getPaths() { return paths; }
        public void setPaths(List<String> paths) { this.paths = paths; }
    }

    @PostMapping
    public Folder createFolder(Principal principal, @RequestBody FolderRequest request) {
        UserAccount owner = getUser(principal);
        return folderService.createFolder(request.getName(), owner, request.getParentId());
    }

    @GetMapping("/templates")
    public List<FolderTemplate> listTemplates() {
        return folderService.getAllTemplates();
    }

    @PostMapping("/templates")
    public FolderTemplate createTemplate(@RequestBody TemplateRequest request) {
        return folderService.createTemplate(request.getName(), request.getPaths());
    }

    @PostMapping("/apply-template/{templateId}")
    public void applyTemplate(Principal principal, @PathVariable Long templateId) {
        UserAccount owner = getUser(principal);
        folderService.applyTemplate(templateId, owner);
    }

    @GetMapping
    public List<Folder> listRootFolders(Principal principal) {
        UserAccount owner = getUser(principal);
        return folderService.getRootFolders(owner);
    }

    @GetMapping("/{id}/subfolders")
    public List<Folder> listSubfolders(Principal principal, @PathVariable Long id) {
        UserAccount owner = getUser(principal);
        return folderService.getSubfolders(owner, id);
    }

    @DeleteMapping("/{id}")
    public void deleteFolder(Principal principal, @PathVariable Long id) {
        UserAccount owner = getUser(principal);
        folderService.deleteFolder(id, owner);
    }

    private UserAccount getUser(Principal principal) {
        return userRepository.findByUsername(principal.getName())
            .orElseThrow(() -> new RuntimeException("User not found"));
    }
}
