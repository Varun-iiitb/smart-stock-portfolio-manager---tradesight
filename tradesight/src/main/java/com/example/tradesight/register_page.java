package com.example.tradesight;

import javafx.animation.TranslateTransition;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import javafx.util.Duration;

public class register_page {

    public Parent getLayout(Stage window) {
        // Create GridPane for form
        GridPane grid = new GridPane();
        grid.setPadding(new Insets(20));
        grid.setVgap(10);
        grid.setHgap(10);
        grid.setAlignment(Pos.CENTER);

        // Error message
        Label errorMessage = new Label("Passwords don't match");
        errorMessage.setStyle("-fx-text-fill: red;");
        errorMessage.setVisible(false);
        GridPane.setConstraints(errorMessage, 0, 7);

        Label errormessage1 = new Label("Username already exists");
        errormessage1.setStyle("-fx-text-fill: red;");
        errormessage1.setVisible(false);
        GridPane.setConstraints(errormessage1, 0, 7);

        // Title
        Label title = new Label("Sign Up");
        title.getStyleClass().add("title");
        GridPane.setConstraints(title, 0, 0);

        // Input fields
        TextField username = new TextField();
        username.setPromptText("Username");
        username.getStyleClass().add("username-btn");
        GridPane.setConstraints(username, 0, 1);

        TextField email = new TextField();
        email.setPromptText("Email");
        email.getStyleClass().add("username-btn");
        GridPane.setConstraints(email, 0, 2);

        PasswordField password = new PasswordField();
        password.setPromptText("Password");
        password.getStyleClass().add("password-btn");

        TextField password1 = new TextField();
        password1.textProperty().bindBidirectional(password.textProperty());
        password1.setVisible(false);
        password1.setManaged(false);
        password1.getStyleClass().add("password-btn");

        Button visible = new  Button("👁");
        visible.setStyle("-fx-background-color: white");
        visible.setPrefHeight(45);
        visible.setOnAction(event -> {
            password.setVisible(false);
            password.setManaged(false);
            password1.setVisible(true);
            password1.setManaged(true);
        });

        HBox hbox = new HBox(10);
        hbox.setSpacing(10);
        hbox.setPadding(new Insets(10));
        hbox.getChildren().addAll(password, password1, visible);

        GridPane.setConstraints(hbox, 0, 3);

        PasswordField confirmPassword = new PasswordField();
        confirmPassword.setPromptText("Confirm Password");
        confirmPassword.getStyleClass().add("password-btn");

        TextField confirmPassword1 = new TextField();
        confirmPassword1.textProperty().bindBidirectional(confirmPassword.textProperty());
        confirmPassword1.setVisible(false);
        confirmPassword1.setManaged(false);
        confirmPassword1.getStyleClass().add("password-btn");

        Button visible1 = new  Button("👁");
        visible1.setStyle("-fx-background-color: white;");
        visible1.setPrefHeight(45);
        visible1.setOnAction(event -> {
            confirmPassword.setVisible(false);
            confirmPassword.setManaged(false);
            confirmPassword1.setVisible(true);
            confirmPassword1.setManaged(true);
        });

        HBox hbox1 = new HBox(10);
        hbox1.setSpacing(10);
        hbox1.setPadding(new Insets(10));
        hbox1.getChildren().addAll(confirmPassword, confirmPassword1, visible1);
        GridPane.setConstraints(hbox1, 0, 4);


        // Sign Up button
        Button signupButton = new Button("Sign up");
        GridPane.setConstraints(signupButton, 0, 5);
        signupButton.getStyleClass().add("sign-btn");

        signupButton.setOnAction(e -> {
            String request = registration_verification.registerUser(username.getText(), password.getText(), email.getText());
            if (!password.getText().equals(confirmPassword.getText())) {
                errorMessage.setVisible(true);
                password.clear();
                confirmPassword.clear();
            }
            else if(request.equals("registration successful")){
                dashboard dash = new dashboard();
                Scene dashscene = new Scene(dash.getlayout(username.getText(),window));
                dashscene.getStylesheets().add(getClass().getResource("/styles.css").toExternalForm());
                window.setScene(dashscene);
                window.setFullScreen(true);
                window.setFullScreenExitHint("");
            }
            else if (request.equals("user already exists")){
                errormessage1.setVisible(true);
                username.clear();
                password.clear();
                email.clear();
                confirmPassword.clear();
            }
        });

        // Already have an account
        Label newLabel = new Label("Already have an account?");
        newLabel.setStyle("-fx-font-size: 16px; -fx-text-fill: white; -fx-effect: dropshadow(gaussian, rgba(0,0,0,0.8), 2, 0.5, 0, 0); -fx-font-weight: bold;");
        GridPane.setConstraints(newLabel, 0, 6);

        Button loginButton = new Button("Login");
        loginButton.getStyleClass().add("login-btn");
        GridPane.setConstraints(loginButton, 1, 6);

        loginButton.setOnAction(e -> {
            TranslateTransition slideOut = new TranslateTransition(Duration.millis(400), grid);
            slideOut.setFromX(0);
            slideOut.setToX(600);
            slideOut.setOnFinished(event -> {
                login_page login = new login_page();
                try {
                    login.start(window);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            });
            slideOut.play();
        });

        // Add all nodes
        grid.getChildren().addAll(title, username, email, hbox, hbox1, signupButton,
                newLabel, loginButton, errorMessage);

        // Wrap in StackPane for animation
        // ✅ Load background image
        Image backgroundImg = new Image(getClass().getResource("/background.jpg").toExternalForm());
        BackgroundImage bgImage = new BackgroundImage(
                backgroundImg,
                BackgroundRepeat.NO_REPEAT,
                BackgroundRepeat.NO_REPEAT,
                BackgroundPosition.CENTER,
                new BackgroundSize(100, 100, true, true, false, true)
        );

// ✅ Wrap in StackPane for animation and set background
        StackPane root = new StackPane(grid);
        root.setBackground(new Background(bgImage));

        // Initial slide-in animation
        grid.setTranslateX(600);
        TranslateTransition slideIn = new TranslateTransition(Duration.millis(400), grid);
        slideIn.setFromX(600);
        slideIn.setToX(0);
        slideIn.play();

        return root;
    }
}
