package com.cyber.securefilesharing.model;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;

@Entity
public class FolderTemplate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;

    @ElementCollection
    @CollectionTable(name = "folder_template_paths", joinColumns = @JoinColumn(name = "template_id"))
    @Column(name = "path")
    private List<String> folderPaths = new ArrayList<>();

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public List<String> getFolderPaths() { return folderPaths; }
    public void setFolderPaths(List<String> folderPaths) { this.folderPaths = folderPaths; }
}
