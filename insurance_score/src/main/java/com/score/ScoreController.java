package com.score;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.ui.Model;

@Controller
public class ScoreController {
	@GetMapping("/score")
	public String welcome(Model model) {
		model.addAttribute("bucket", new Bucket());
		return "score";
	}

	@PostMapping("/score")
	public String calculateScore(@ModelAttribute Bucket bucket) {
		System.out.println(bucket.getName());
		String command = "python score.py " + bucket.getName();
		Process p;
		
		try {
			p = Runtime.getRuntime().exec(command);
			p.waitFor();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return "score";
	}
	
	@GetMapping("/get_score")
    public @ResponseBody String score() {
		String url = "https://veqxp1wam5.execute-api.us-east-1.amazonaws.com/prod/get_score";
		URL obj;
		StringBuffer response = null;
		try {
			obj = new URL(url);
			HttpURLConnection con = (HttpURLConnection) obj.openConnection();

			// optional default is GET
			con.setRequestMethod("GET");
			String USER_AGENT = "Mozilla/5.0";
			//add request header
			con.setRequestProperty("User-Agent", USER_AGENT);

			int responseCode = con.getResponseCode();
			System.out.println("\nSending 'GET' request to URL : " + url);
			System.out.println("Response Code : " + responseCode);

			BufferedReader in = new BufferedReader(
			        new InputStreamReader(con.getInputStream()));
			String inputLine;
			response = new StringBuffer();

			while ((inputLine = in.readLine()) != null) {
				response.append(inputLine);
			}
			in.close();

			//print result
			System.out.println(response.toString());
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
        
		return response.toString();
    }
	
	
	@GetMapping("/result")
	public String result(Model model) {
		//model.addAttribute("bucket", new Bucket());
		return "result";
	}
}
