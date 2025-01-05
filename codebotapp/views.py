from django.http import HttpResponse
from django.shortcuts import render, redirect
from github import Github
from django.core.cache import cache
from django.conf import settings
import os, requests
import google.generativeai as genai



def index(request):
    if request.method == 'POST':
        # Get the input string from the form
        ghtkn = os.getenv("GH_API_TOKEN")
        gh_token = Github(ghtkn)
        input_string = request.POST.get('input_string') #repo = "microsoft/vscode"
        # Cache the repo name, gh token, llm token
        cache.set('code_repo', input_string, timeout=60*150)  # Cache for 15 minutes
        cache.set('gh_token', gh_token, timeout=60*150)  # Cache for 15 minutes

        return redirect('viewrepo')  # Redirect to view repo PRs

    return render(request, 'index.html')


def viewrepo(request):
    
    code_repo = cache.get('code_repo')
    g = cache.get('gh_token')
    repo = g.get_repo(code_repo)

    pulls = repo.get_pulls()
    
    return render(request, 'repo.html', {'pulls': pulls})


def view_pull_request(request, pr_number):
    try:
        code_repo = cache.get('code_repo')
        g = cache.get('gh_token')
        repo = g.get_repo(code_repo)
  
        pull_request = repo.get_pull(pr_number)
        files_changed = pull_request.get_files()

        # Create a context with PR details
        context = {
            "title": pull_request.title,
            "pull_request_id": pr_number,
            "user": pull_request.user.login,
            "created_at": pull_request.created_at,
            "state": pull_request.state,
            "body": pull_request.body,
            "html_url": pull_request.html_url,
            "files_changed": files_changed,

        }
      
    except Exception as e:
        context = {"error": f"Error fetching pull request: {e}"}

    return render(request, "pull_request_detail.html", context)


def llm_review(request):
	gmtkn = os.getenv("GEMINI_API_TOKEN")
	genai.configure(api_key= gmtkn)
	# Create the model
	generation_config = {
  		"temperature": 1,
  		"top_p": 0.95,
  		"top_k": 40,
  		"max_output_tokens": 8192,
  		"response_mime_type": "text/plain",
	}

	model = genai.GenerativeModel(
  		model_name="gemini-2.0-flash-exp",
  		generation_config=generation_config,
	)

	chat_session = model.start_chat(
  		history=[
  		]
	)
	
	pr_number = request.POST.get('pull_request_id')
	pr_number = int(pr_number)
	
	if not pr_number:

		return render(request, "error_page.html", {"message": "Pull request ID is missing."})
	
	code_repo = cache.get('code_repo')
	g = cache.get('gh_token')
	repo = g.get_repo(code_repo)

	pull_request = repo.get_pull(pr_number)
	files_changed = pull_request.get_files()

	context = {}

	for file in files_changed:
		print(f"File: {file.filename}")
		prompt_role_tl = "You are a technical lead reviewing code and providing comments.Be to the point in the response. Please review the following Pull Requests and provide your feedback:"
		prompt = prompt_role_tl + " " + file.patch
		#print(prompt)
		response = chat_session.send_message(prompt)
		text_response = response.text
		context[file.filename] = text_response
		
		#print(f"File: {response}")
	 	
	print(f"All file items: {context}")




	return render(request, "code_review_response.html", {'my_dict': context})




# def llm_review(request):
#     my_dict = {
#         'Name': 'John Doe',
#         'Age': 30,
#         'Location': 'Austin, TX',
#         'Job': 'Data Scientist'
#     }
#     return render(request, 'code_review_response.html', {'my_dict': my_dict})
