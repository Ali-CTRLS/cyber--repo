package com.cyber.securefilesharing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import com.cyber.securefilesharing.service.FolderService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class SecureFileSharingApplication {
    public static void main(String[] args) {
        SpringApplication.run(SecureFileSharingApplication.class, args);
    }

    @Bean
    public CommandLineRunner seedTemplates(FolderService folderService) {
        return args -> {
            folderService.createTemplate("Project Structure", java.util.Arrays.asList(
                "Documents",
                "Documents/Specs",
                "Documents/Feedback",
                "Source",
                "Assets",
                "Assets/Images",
                "Assets/Videos"
            ));
            folderService.createTemplate("Simple Archive", java.util.Arrays.asList(
                "Old",
                "Current",
                "Temp"
            ));
        };
    }
}
