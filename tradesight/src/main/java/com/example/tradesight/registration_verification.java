package com.example.tradesight;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class registration_verification {
    public static String registerUser(String username, String password, String email) {
        try{
            // json string
            String jsonbody = String.format(
                    "{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\"}", username, password, email
            );

            // creating a HTTP request
            HttpRequest request = HttpRequest.newBuilder().uri(URI.create("http://localhost:5000/register")).header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(jsonbody)).build();
            HttpClient httpClient = HttpClient.newHttpClient();
            HttpResponse<String> response = httpClient.send(request,HttpResponse.BodyHandlers.ofString());

            String responseBody = response.body();

            if (response.statusCode() == 201) {
                return "registration successful";
            }
            else if (response.statusCode() == 400) {
                return "user already exists";
            }
            else{
                return "Something went wrong";
            }
        } catch (Exception e) {
            return "Error while connecting to the server";
        }
    }
}
