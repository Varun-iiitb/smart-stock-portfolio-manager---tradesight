package com.example.tradesight;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.Stage;

import java.io.*;

public class login_page extends Application {
    Stage window;

    @Override
    public void start(Stage primaryStage) {
        startBackend();
        window = primaryStage;
        window.setTitle("Tradesight");
        Image icon = new Image(getClass().getResource("/tradesight_icon.png").toExternalForm());
        window.getIcons().add(icon);


        // Load image
        Image logo = new Image(getClass().getResourceAsStream("/tradesight.png"));
        ImageView logoView = new ImageView(logo);
        logoView.setPreserveRatio(true);
        logoView.setFitWidth(300);

        // Username
        TextField username = new TextField();
        username.setPromptText("Username");
        username.setMaxWidth(250);
        username.getStyleClass().add("username-btn");

        Label errormessage = new Label("Invalid username or password");
        errormessage.setStyle("-fx-text-fill: red;");
        errormessage.setVisible(false);

        // Password
        PasswordField password = new PasswordField();
        password.setPromptText("Password");
        password.getStyleClass().add("password-btn");

        TextField password1 = new TextField();
        password1.textProperty().bindBidirectional(password.textProperty());
        password1.setVisible(false);
        password1.setManaged(false);
        password1.getStyleClass().add("password-btn");

        Button visible1 = new Button("👁");
        visible1.setPrefHeight(45);
        visible1.setStyle("-fx-background-color: white;");
        visible1.setOnAction(e -> {
            password.setVisible(false);
            password.setManaged(false);
            password1.setVisible(true);
            password1.setManaged(true);
        });

        HBox hbox1 = new HBox(10);
        hbox1.setAlignment(Pos.CENTER);
        hbox1.getChildren().addAll(password, password1, visible1);

        // Login Button
        Button loginButton = new Button("Login");
        loginButton.getStyleClass().add("login-btn");

        loginButton.setOnAction(e -> {
            String request = login_verification.loginUser(username.getText(), password1.getText());
            if (request.equals("Login successful")) {
                System.out.println("y2");
                dashboard dash = new dashboard();
                Scene dashscene = new Scene(dash.getlayout(username.getText(), window));
                dashscene.getStylesheets().add(getClass().getResource("/styles.css").toExternalForm());

                window.setScene(dashscene);
                window.setFullScreenExitHint("");
                window.setFullScreen(true); // ✅ Moved after setting the scene to avoid flicker
            } else if (request.equals("Invalid credentials")) {
                errormessage.setVisible(true);
                username.clear();
                password.clear();
            }
        });

        // Register section
        Label newLabel = new Label("Don't have an account?");
        newLabel.setStyle("-fx-font-size: 16px; -fx-text-fill: white; -fx-effect: dropshadow(gaussian, rgba(0,0,0,0.8), 2, 0.5, 0, 0); -fx-font-weight: bold;");
        Button registerButton = new Button("Sign up");
        registerButton.getStyleClass().add("signup-btn");

        registerButton.setOnAction(e -> {
            register_page regPage = new register_page();
            Scene registerScene = new Scene(regPage.getLayout(window));
            registerScene.getStylesheets().add(getClass().getResource("/register.css").toExternalForm());

            window.setScene(registerScene);
            window.setFullScreenExitHint("");
            window.setFullScreen(true); // ✅ Moved after setting the scene
        });

        HBox hbox = new HBox(10, newLabel, registerButton);
        hbox.setAlignment(Pos.CENTER);

        // Layout
        VBox layout = new VBox(20, logoView, username, hbox1, loginButton, hbox);
        layout.setAlignment(Pos.TOP_CENTER);
        layout.setPadding(new Insets(30));
        layout.setSpacing(25);

        // Background image
        Image backgroundImg = new Image(getClass().getResource("/background.jpg").toExternalForm());
        BackgroundImage bgImage = new BackgroundImage(
                backgroundImg,
                BackgroundRepeat.NO_REPEAT,
                BackgroundRepeat.NO_REPEAT,
                BackgroundPosition.CENTER,
                new BackgroundSize(100, 100, true, true, false, true)
        );
        layout.setBackground(new Background(bgImage));

        // Scene
        Scene scene = new Scene(layout);
        scene.getStylesheets().add(getClass().getResource("/login.css").toExternalForm());


        window.setScene(scene);
        window.setFullScreenExitHint("");
        window.setFullScreen(true); // ✅ Moved after setting the scene
        window.show();

        window.fullScreenProperty().addListener((obs, wasFullScreen, isNowFullScreen) -> {
            if (!isNowFullScreen) {
                // User exited fullscreen — lock to a fixed size
                window.setWidth(1280);
                window.setHeight(800);
                window.setResizable(false); // optional: prevent resizing
                window.centerOnScreen();    // optional: center the window
            }
        });
    }
    private void startBackend() {
        try {
            // Get current directory (tradesight_app/tradesight)
            String currentDir = new File(".").getCanonicalPath(); // This gets C:\Users\varun\OneDrive\Desktop\tradesight_app\tradesight
            System.out.println("📁 Current Directory: " + currentDir);

            // Get the parent directory (C:\Users\varun\OneDrive\Desktop\tradesight_app)
            File parentDir = new File(currentDir).getParentFile(); // <--- ADD THIS LINE

            // Construct the correct path to app.py from the parent directory
            File backendFile = new File(parentDir, "backend/app.py").getCanonicalFile(); // <--- CHANGE THIS LINE
            System.out.println("📄 Looking for app.py at: " + backendFile.getAbsolutePath());

            if (!backendFile.exists()) {
                System.err.println("❌ app.py not found at: " + backendFile.getAbsolutePath());
                return;
            }

            // Set backend dir as working directory for Flask
            File backendDir = backendFile.getParentFile();

            // Start the Python process
            ProcessBuilder pb = new ProcessBuilder("python", "app.py");
            pb.directory(backendDir);
            pb.redirectErrorStream(true);

            Process process = pb.start();

            // Read logs
            new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()));
                     BufferedWriter logWriter = new BufferedWriter(
                             new FileWriter("flask_debug.log", true))) {

                    String line;
                    while ((line = reader.readLine()) != null) {
                        System.out.println("[Flask] " + line);
                        logWriter.write(line);
                        logWriter.newLine();
                        logWriter.flush();
                    }
                } catch (IOException e) {
                    System.err.println("❌ Error reading Flask backend output:");
                    e.printStackTrace();
                }
            }).start();

            System.out.println("✅ Flask backend started.");

        } catch (IOException e) {
            System.err.println("❌ Could not start Flask backend.");
            e.printStackTrace();
        }
    }
    public static void main(String[] args) {
        launch(args);
    }
}
