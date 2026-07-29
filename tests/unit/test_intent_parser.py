from ums.recall.intent_parser import parse_intent


class TestParseIntent:
    def test_empty_string_returns_default(self):
        result = parse_intent("")
        assert result.type == "general"
        assert result.project is None
        assert result.focus == ["preferences", "projects", "beliefs"]

    def test_whitespace_only_returns_default(self):
        result = parse_intent("   ")
        assert result.type == "general"
        assert result.project is None

    def test_code_review_keyword_review(self):
        result = parse_intent("review the latest PR")
        assert result.type == "code_review"

    def test_code_review_keyword_code(self):
        result = parse_intent("write some code for the module")
        assert result.type == "code_review"

    def test_code_review_keyword_debug(self):
        result = parse_intent("debug the connection issue")
        assert result.type == "code_review"

    def test_code_review_keyword_fix(self):
        result = parse_intent("fix the null pointer bug")
        assert result.type == "code_review"

    def test_code_review_keyword_implement(self):
        result = parse_intent("implement the recall engine")
        assert result.type == "code_review"

    def test_information_keyword_what(self):
        result = parse_intent("what is the current status")
        assert result.type == "information"

    def test_information_keyword_how(self):
        result = parse_intent("how does the system work")
        assert result.type == "information"

    def test_information_keyword_explain(self):
        result = parse_intent("explain the architecture")
        assert result.type == "information"

    def test_information_keyword_tell_me_about(self):
        result = parse_intent("tell me about the project")
        assert result.type == "information"

    def test_default_general(self):
        result = parse_intent("run the build script")
        assert result.type == "general"

    def test_detects_project(self):
        result = parse_intent("review project alpha")
        assert result.project == "alpha"

    def test_detects_repo(self):
        result = parse_intent("debug repo myapp")
        assert result.project == "myapp"

    def test_detects_app(self):
        result = parse_intent("fix app frontend")
        assert result.project == "frontend"

    def test_project_with_underscores(self):
        result = parse_intent("review project my_project")
        assert result.project == "my_project"

    def test_project_with_hyphens(self):
        result = parse_intent("review project my-project")
        assert result.project == "my-project"

    def test_code_review_with_project(self):
        result = parse_intent("fix bug in project core")
        assert result.type == "code_review"
        assert result.project == "core"

    def test_information_with_project(self):
        result = parse_intent("tell me about project ums")
        assert result.type == "information"
        assert result.project == "ums"
