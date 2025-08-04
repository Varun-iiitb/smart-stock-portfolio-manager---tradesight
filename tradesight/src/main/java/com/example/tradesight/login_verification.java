package com.example.tradesight;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class login_verification {
    public static String loginUser(String username, String password) {
        try{
            System.out.println("y");
            String jsonbody = String.format("{\"username\":\"%s\",\"password\":\"%s\"}", username, password);

            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/login")).header("Content-Type", "application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request,HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();

            if (response.statusCode() == 200 && responseBody.contains("Login successful")) {
                System.out.println("y1");
                return "Login successful";
            }

            else if (response.statusCode() == 401 && responseBody.contains("Invalid credentials")) {
                System.out.println("y2");
                return "Invalid credentials";
            }
            else{
                System.out.println("y3");
                return "Something went wrong";
            }
        } catch (Exception e) {
            return "Error while connecting to the server";
        }
    }
}
