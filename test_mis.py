"""
Cyber Incident MIS — Selenium Test Suite
==========================================
Tests all major features across all four roles.

Requirements:
    pip install selenium
    (Selenium 4.6+ handles ChromeDriver automatically)

Run:
    Terminal 1:  python app.py
    Terminal 2:  python test_mis.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import sys

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

BASE_URL = "http://localhost:5000"

USERS = {
    "reporter":   {"email": "reporter@mis.com",   "password": "reporter123"},
    "analyst":    {"email": "analyst@mis.com",    "password": "analyst123"},
    "admin":      {"email": "admin@mis.com",       "password": "admin123"},
    "management": {"email": "management@mis.com", "password": "management123"},
}

# ─────────────────────────────────────────────
# TEST RUNNER
# ─────────────────────────────────────────────

passed = []
failed = []
errors = []

def test(name, fn):
    try:
        fn()
        passed.append(name)
        print(f"  ✓  {name}")
    except AssertionError as e:
        failed.append((name, str(e)))
        print(f"  ✗  {name}")
        print(f"       → {e}")
    except Exception as e:
        msg = str(e).split('\n')[0]
        errors.append((name, msg))
        print(f"  !  {name}")
        print(f"       → {msg}")

def section(title):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")

def summary():
    total = len(passed) + len(failed) + len(errors)
    print(f"\n{'═'*55}")
    print(f"  TEST SUMMARY")
    print(f"{'═'*55}")
    print(f"  Total:   {total}")
    print(f"  Passed:  {len(passed)}  ✓")
    print(f"  Failed:  {len(failed)}  ✗")
    print(f"  Errors:  {len(errors)}  !")
    if failed:
        print(f"\n  FAILED TESTS:")
        for name, msg in failed:
            print(f"    ✗ {name}")
            print(f"      {msg}")
    if errors:
        print(f"\n  ERROR TESTS:")
        for name, msg in errors:
            print(f"    ! {name}")
            print(f"      {msg}")
    print(f"{'═'*55}\n")

# ─────────────────────────────────────────────
# BROWSER HELPERS
# ─────────────────────────────────────────────

def wait_for(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def wait_clickable(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )

def login(driver, role):
    """Always logout first, then navigate to login and sign in fresh."""
    driver.get(BASE_URL + "/logout")
    time.sleep(0.5)
    driver.get(BASE_URL)
    wait_for(driver, By.NAME, "email")
    driver.find_element(By.NAME, "email").clear()
    driver.find_element(By.NAME, "email").send_keys(USERS[role]["email"])
    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(USERS[role]["password"])
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(1.5)

def logout(driver):
    driver.get(BASE_URL + "/logout")
    time.sleep(0.5)

def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text

def click_tab(driver, tab_text):
    """Click admin tab by partial text match on nav-link elements."""
    tabs = driver.find_elements(By.CSS_SELECTOR, ".tab-bar .nav-link")
    for tab in tabs:
        if tab_text.lower() in tab.text.lower():
            driver.execute_script("arguments[0].click();", tab)
            time.sleep(0.8)
            return
    raise Exception(f"Tab containing '{tab_text}' not found in tab bar")

def get_driver():
    options = Options()
    # options.add_argument("--headless")  # Uncomment for silent mode
    options.add_argument("--window-size=1400,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver

# ─────────────────────────────────────────────
# AUTH TESTS
# ─────────────────────────────────────────────

def run_auth_tests(driver):
    section("AUTH TESTS")

    def test_invalid_login():
        driver.get(BASE_URL)
        wait_for(driver, By.NAME, "email")
        driver.find_element(By.NAME, "email").send_keys("wrong@email.com")
        driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        time.sleep(1)
        assert "Invalid" in body_text(driver) or "invalid" in body_text(driver).lower(), \
            "Expected error message for invalid login"

    def test_reporter_login_redirect():
        login(driver, "reporter")
        assert "/reporter" in driver.current_url, \
            f"Reporter should land on /reporter, got {driver.current_url}"

    def test_analyst_login_redirect():
        login(driver, "analyst")
        assert "/analyst" in driver.current_url, \
            f"Analyst should land on /analyst, got {driver.current_url}"

    def test_admin_login_redirect():
        login(driver, "admin")
        assert "/admin" in driver.current_url, \
            f"Admin should land on /admin, got {driver.current_url}"

    def test_management_login_redirect():
        login(driver, "management")
        assert "/management" in driver.current_url, \
            f"Management should land on /management, got {driver.current_url}"

    def test_logout_clears_session():
        login(driver, "reporter")
        logout(driver)
        driver.get(BASE_URL + "/reporter")
        time.sleep(1)
        assert "/reporter" not in driver.current_url, \
            "After logout, /reporter should redirect to login"

    def test_reporter_cannot_access_admin():
        login(driver, "reporter")
        driver.get(BASE_URL + "/admin")
        time.sleep(1)
        assert "/admin" not in driver.current_url, \
            "Reporter should not be able to access /admin"

    def test_analyst_cannot_access_management():
        login(driver, "analyst")
        driver.get(BASE_URL + "/management")
        time.sleep(1)
        assert "/management" not in driver.current_url, \
            "Analyst should not be able to access /management"

    def test_register_page_loads():
        driver.get(BASE_URL + "/register")
        wait_for(driver, By.NAME, "name")
        assert "Create" in body_text(driver) or "Register" in body_text(driver), \
            "Register page should load"

    test("Invalid login shows error message",         test_invalid_login)
    test("Reporter login redirects to /reporter",     test_reporter_login_redirect)
    test("Analyst login redirects to /analyst",       test_analyst_login_redirect)
    test("Admin login redirects to /admin",           test_admin_login_redirect)
    test("Management login redirects to /management", test_management_login_redirect)
    test("Logout clears session",                     test_logout_clears_session)
    test("Reporter cannot access /admin",             test_reporter_cannot_access_admin)
    test("Analyst cannot access /management",         test_analyst_cannot_access_management)
    test("Register page loads",                       test_register_page_loads)

# ─────────────────────────────────────────────
# REPORTER TESTS
# ─────────────────────────────────────────────

def run_reporter_tests(driver):
    section("REPORTER TESTS")

    login(driver, "reporter")
    wait_for(driver, By.TAG_NAME, "body")

    def test_dashboard_loads():
        assert "Reporter Dashboard" in body_text(driver), \
            "Reporter dashboard heading should be visible"

    def test_stat_cards():
        assert "Total Submitted" in body_text(driver), \
            "Stat cards should be visible"

    def test_submit_form_visible():
        assert "Report New Incident" in body_text(driver), \
            "Submit form heading should be visible"

    def test_incidents_table_visible():
        assert "My Submitted Incidents" in body_text(driver), \
            "Incidents table should be visible"

    def test_submit_incident():
        Select(driver.find_element(By.NAME, "type")).select_by_visible_text("Phishing")
        Select(driver.find_element(By.CSS_SELECTOR, "select[name='severity']")).select_by_value("High")
        driver.find_element(By.NAME, "affected_resources").send_keys("Email Server, Outlook")
        driver.find_element(By.NAME, "affected_systems").send_keys("Windows 10, Outlook 2019")
        driver.find_element(By.NAME, "no_of_users_affected").send_keys("3")
        driver.find_element(By.NAME, "location").send_keys("Mumbai HQ")
        driver.find_element(By.NAME, "estimated_impact").send_keys("Credential theft")
        driver.find_element(By.NAME, "description").send_keys(
            "Selenium automated test incident. Employee received phishing email and clicked link."
        )
        driver.execute_script(
            "document.querySelector('[name=occurred_date]').value='2024-04-01';"
            "document.querySelector('[name=occurred_time]').value='09:00';"
        )
        driver.execute_script("""
            const form = document.getElementById('incidentForm');
            const h = document.createElement('input');
            h.type='hidden'; h.name='occurred_at'; h.value='2024-04-01 09:00';
            form.appendChild(h);
            form.submit();
        """)
        time.sleep(2.5)

    def test_success_banner():
        bt = body_text(driver)
        assert "Successfully" in bt or "registered" in bt.lower() or "INC-" in bt, \
            "Success banner should appear after submission"

    def test_incident_id_generated():
        assert "INC-" in body_text(driver), \
            "Incident ID in INC-XXX format should appear"

    def test_ticket_link():
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Print")
        ticket_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Ticket")
        assert len(links) > 0 or len(ticket_links) > 0, \
            "Ticket/Print link should appear"

    def test_incident_in_table():
        assert "Phishing" in body_text(driver), \
            "Submitted incident should appear in table"

    def test_ticket_page_loads():
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Print")
        if links:
            href = links[0].get_attribute("href")
            driver.execute_script(f"window.open('{href}','_blank');")
            time.sleep(1.5)
            driver.switch_to.window(driver.window_handles[-1])
            bt = body_text(driver)
            assert "Cyber Incident" in bt or "INC-" in bt, \
                "Ticket page should contain incident details"
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    def test_reporter_logout():
        logout(driver)
        assert "/reporter" not in driver.current_url, "Should be logged out"

    test("Reporter dashboard loads",         test_dashboard_loads)
    test("Reporter sees stat cards",         test_stat_cards)
    test("Reporter sees submit form",        test_submit_form_visible)
    test("Reporter sees incidents table",    test_incidents_table_visible)
    test("Reporter can submit incident",     test_submit_incident)
    test("Success banner shown",            test_success_banner)
    test("Incident ID generated (INC-XXX)", test_incident_id_generated)
    test("Ticket print link present",        test_ticket_link)
    test("New incident appears in table",    test_incident_in_table)
    test("Ticket page loads with details",   test_ticket_page_loads)
    test("Reporter logout",                  test_reporter_logout)

# ─────────────────────────────────────────────
# ANALYST TESTS
# ─────────────────────────────────────────────

def run_analyst_tests(driver):
    section("ANALYST TESTS")

    login(driver, "analyst")
    wait_for(driver, By.TAG_NAME, "body")

    def test_dashboard_loads():
        assert "Analyst Dashboard" in body_text(driver), \
            "Analyst dashboard heading should be visible"

    def test_stat_cards():
        assert "Total Assigned" in body_text(driver), \
            "Analyst stat cards should be visible"

    def test_sees_assigned_incidents():
        assert "INC-" in body_text(driver), \
            "Analyst should see assigned incident IDs"

    def test_sees_all_statuses():
        bt = body_text(driver)
        assert any(s in bt for s in ["Under Investigation","Resolved","Closed","Reported"]), \
            "Analyst should see incidents with various statuses"

    def test_sees_incident_details():
        bt = body_text(driver)
        assert any(w in bt for w in ["Occurred","Affected","Description","Reporter"]), \
            "Incident cards should show full details"

    def test_investigate_button_visible():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Investigate')]")
        assert len(btns) > 0, "Investigate button should be visible for active incidents"

    def test_investigate_opens_form():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Investigate')]")
        if btns:
            driver.execute_script("arguments[0].scrollIntoView(true);", btns[0])
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(1)
            WebDriverWait(driver, 8).until(
                lambda d: any(f.is_displayed() for f in d.find_elements(By.NAME, "findings"))
            )
            visible = [f for f in driver.find_elements(By.NAME, "findings") if f.is_displayed()]
            assert len(visible) > 0, "Findings field should be visible after clicking Investigate"

    def test_form_has_all_fields():
        findings   = [f for f in driver.find_elements(By.NAME, "findings")           if f.is_displayed()]
        actions    = [f for f in driver.find_elements(By.NAME, "actions_taken")      if f.is_displayed()]
        resolution = [f for f in driver.find_elements(By.NAME, "resolution_details") if f.is_displayed()]
        assert len(findings) > 0,   "Findings field should be visible"
        assert len(actions) > 0,    "Actions taken field should be visible"
        assert len(resolution) > 0, "Resolution details field should be visible"

    def test_fill_and_save_investigation():
        findings_fields = [f for f in driver.find_elements(By.NAME, "findings") if f.is_displayed()]
        if not findings_fields:
            btns = driver.find_elements(By.XPATH, "//button[contains(.,'Investigate')]")
            if btns:
                driver.execute_script("arguments[0].click();", btns[0])
                time.sleep(1)
                findings_fields = [f for f in driver.find_elements(By.NAME, "findings") if f.is_displayed()]
        if findings_fields:
            driver.execute_script("arguments[0].value = arguments[1];",
                findings_fields[0], "Selenium test: Phishing traced to spoofed domain.")
            actions = [f for f in driver.find_elements(By.NAME, "actions_taken") if f.is_displayed()]
            if actions:
                driver.execute_script("arguments[0].value = arguments[1];",
                    actions[0], "Selenium test: Blocked domain, reset passwords.")
            res = [f for f in driver.find_elements(By.NAME, "resolution_details") if f.is_displayed()]
            if res:
                driver.execute_script("arguments[0].value = arguments[1];",
                    res[0], "Selenium test: Incident resolved.")
            status_selects = [s for s in driver.find_elements(By.NAME, "status") if s.is_displayed()]
            if status_selects:
                Select(status_selects[0]).select_by_visible_text("Under Investigation")
            save_btns = [b for b in driver.find_elements(
                By.XPATH, "//button[contains(.,'Save Investigation')]") if b.is_displayed()]
            if save_btns:
                driver.execute_script("arguments[0].click();", save_btns[0])
                time.sleep(2)
        assert "Analyst Dashboard" in body_text(driver), \
            "Should stay on analyst dashboard after saving"

    def test_analyst_logout():
        logout(driver)
        assert "/analyst" not in driver.current_url, "Should be logged out"

    test("Analyst dashboard loads",                 test_dashboard_loads)
    test("Analyst sees stat cards",                 test_stat_cards)
    test("Analyst sees assigned incidents",         test_sees_assigned_incidents)
    test("Analyst sees incidents of all statuses",  test_sees_all_statuses)
    test("Incident cards show full details",        test_sees_incident_details)
    test("Investigate button visible",              test_investigate_button_visible)
    test("Investigate button opens form",           test_investigate_opens_form)
    test("Investigation form has all three fields", test_form_has_all_fields)
    test("Analyst can fill and save investigation", test_fill_and_save_investigation)
    test("Analyst logout",                          test_analyst_logout)

# ─────────────────────────────────────────────
# ADMIN TESTS
# ─────────────────────────────────────────────

def run_admin_tests(driver):
    section("ADMIN TESTS")

    login(driver, "admin")
    wait_for(driver, By.TAG_NAME, "body")

    def test_dashboard_loads():
        assert "Admin Dashboard" in body_text(driver), \
            "Admin dashboard heading should be visible"

    def test_sees_all_incidents():
        assert "All Incidents" in body_text(driver), \
            "Admin should see All Incidents section"
        assert "INC-" in body_text(driver), \
            "Admin should see incident IDs"

    def test_stat_cards():
        assert "Total Incidents" in body_text(driver), \
            "Admin stat cards should be visible"

    def test_classify_button():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Classify')]")
        assert len(btns) > 0, "Classify buttons should be visible"

    def test_classify_opens_panel():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Classify')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", btns[0])
        driver.execute_script("arguments[0].click();", btns[0])
        time.sleep(0.8)
        visible = [s for s in driver.find_elements(By.NAME, "severity_category") if s.is_displayed()]
        assert len(visible) > 0, "Classify panel should open showing severity_category dropdown"

        def test_classify_all_three_fields():
            sev    = [s for s in driver.find_elements(By.NAME, "severity_category") if s.is_displayed()]
            impact = [s for s in driver.find_elements(By.NAME, "impact_level")      if s.is_displayed()]
            prio   = [s for s in driver.find_elements(By.NAME, "priority")          if s.is_displayed()]
            assert len(sev) > 0,    "severity_category dropdown should be visible"
            assert len(impact) > 0, "impact_level dropdown should be visible"
            assert len(prio) > 0,   "priority dropdown should be visible"

    def test_save_classification():
        sev    = [s for s in driver.find_elements(By.NAME, "severity_category") if s.is_displayed()]
        impact = [s for s in driver.find_elements(By.NAME, "impact_level")      if s.is_displayed()]
        prio   = [s for s in driver.find_elements(By.NAME, "priority")          if s.is_displayed()]
        if sev and impact and prio:
            Select(sev[0]).select_by_value("Critical")
            Select(impact[0]).select_by_value("Critical")
            Select(prio[0]).select_by_value("P1 - Critical")
            save = [b for b in driver.find_elements(
                By.XPATH, "//button[contains(.,'Save Classification')]") if b.is_displayed()]
            if save:
                driver.execute_script("arguments[0].click();", save[0])
                time.sleep(2)
        # After reload, verify the saved values appear in the table columns
        bt = body_text(driver)
        assert "Admin Dashboard" in bt, \
            "Should stay on admin dashboard after classification"
        assert "P1 - Critical" in bt, \
            "P1 - Critical priority should appear in table after saving"
        assert "Critical" in bt, \
            "Critical impact should appear in table after saving"

    def test_assign_button():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Assign')]")
        assert len(btns) > 0, "Assign buttons should be visible"

    def test_assign_opens_panel():
        btns = driver.find_elements(By.XPATH, "//button[contains(.,'Assign')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", btns[0])
        driver.execute_script("arguments[0].click();", btns[0])
        time.sleep(0.8)
        visible = [s for s in driver.find_elements(By.NAME, "analyst_id") if s.is_displayed()]
        assert len(visible) > 0, "Assign panel should show analyst dropdown"

    def test_can_assign():
        analyst_sel = [s for s in driver.find_elements(By.NAME, "analyst_id") if s.is_displayed()]
        if analyst_sel:
            Select(analyst_sel[0]).select_by_index(0)
            assign = [b for b in driver.find_elements(
                By.XPATH, "//button[contains(.,'Confirm Assignment')]") if b.is_displayed()]
            if assign:
                driver.execute_script("arguments[0].click();", assign[0])
                time.sleep(2)
        assert "Admin Dashboard" in body_text(driver), \
            "Should stay on admin dashboard after assigning"

    def test_user_management_tab():
        click_tab(driver, "User Management")
        assert "Add New User" in body_text(driver), \
            "User Management tab should show Add New User form"

    def test_add_user():
        click_tab(driver, "User Management")
        fields = [f for f in driver.find_elements(By.CSS_SELECTOR, "input[name='name']") if f.is_displayed()]
        if fields:
            fields[0].clear()
            fields[0].send_keys("Selenium Test User")
        fields = [f for f in driver.find_elements(By.CSS_SELECTOR, "input[name='email']") if f.is_displayed()]
        if fields:
            fields[0].clear()
            fields[0].send_keys("selenium_auto@mis.com")
        fields = [f for f in driver.find_elements(By.CSS_SELECTOR, "input[name='password']") if f.is_displayed()]
        if fields:
            fields[0].clear()
            fields[0].send_keys("test123456")
        role_sel = [s for s in driver.find_elements(By.NAME, "role") if s.is_displayed()]
        if role_sel:
            Select(role_sel[0]).select_by_value("reporter")
        add_btn = [b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Add')]") if b.is_displayed()]
        if add_btn:
            driver.execute_script("arguments[0].click();", add_btn[0])
            time.sleep(2)
        assert "Selenium Test User" in body_text(driver), \
            "New user should appear in user list"

    def test_audit_log_tab():
        click_tab(driver, "Audit Log")
        bt = body_text(driver)
        assert "Total Events" in bt or "Audit Log" in bt, \
            "Audit Log tab should load"

    def test_audit_log_has_entries():
        bt = body_text(driver)
        assert any(w in bt for w in ["Login","Submitted","Classified","Assigned"]), \
            "Audit log should have action entries"

    def test_audit_log_role_badges():
        reporter_badges = driver.find_elements(By.CLASS_NAME, "role-badge-reporter")
        admin_badges    = driver.find_elements(By.CLASS_NAME, "role-badge-admin")
        assert len(reporter_badges) > 0 or len(admin_badges) > 0, \
            "Role colour badges should be present in audit log"

    def test_admin_logout():
        logout(driver)
        assert "/admin" not in driver.current_url, "Should be logged out"

    test("Admin dashboard loads",               test_dashboard_loads)
    test("Admin sees all incidents",            test_sees_all_incidents)
    test("Admin sees stat cards",               test_stat_cards)
    test("Classify button visible",             test_classify_button)
    test("Classify button opens panel",         test_classify_opens_panel)
    test("Classify panel has all three fields", test_classify_all_three_fields)
    test("Admin can save classification",       test_save_classification)
    test("Assign button visible",               test_assign_button)
    test("Assign button opens panel",           test_assign_opens_panel)
    test("Admin can assign incident",           test_can_assign)
    test("User Management tab loads",           test_user_management_tab)
    test("Admin can add new user",              test_add_user)
    test("Audit Log tab loads",                 test_audit_log_tab)
    test("Audit log has entries",               test_audit_log_has_entries)
    test("Audit log shows role colour badges",  test_audit_log_role_badges)
    test("Admin logout",                        test_admin_logout)

# ─────────────────────────────────────────────
# MANAGEMENT TESTS
# ─────────────────────────────────────────────

def run_management_tests(driver):
    section("MANAGEMENT TESTS")

    login(driver, "management")
    wait_for(driver, By.TAG_NAME, "body")

    def test_dashboard_loads():
        assert "Management Dashboard" in body_text(driver), \
            "Management dashboard heading should be visible"

    def test_readonly_notice():
        bt = body_text(driver)
        assert "Read-only" in bt or "read only" in bt.lower(), \
            "Read-only notice should be visible"

    def test_stat_cards_visible():
        bt = body_text(driver)
        assert "Total Incidents" in bt,  "Total Incidents card should be visible"
        assert "Open / Active" in bt,    "Open card should be visible"
        assert "Resolved" in bt,         "Resolved card should be visible"
        assert "Critical Severity" in bt, "Critical card should be visible"

    def test_stat_cards_have_numbers():
        nums = driver.find_elements(By.CLASS_NAME, "num")
        assert len(nums) >= 4, f"Should have at least 4 stat numbers, found {len(nums)}"
        for num in nums[:4]:
            assert num.text.strip().isdigit(), \
                f"Stat number should be a digit, got: '{num.text.strip()}'"

    def test_four_charts_present():
        charts = driver.find_elements(By.TAG_NAME, "canvas")
        assert len(charts) == 4, f"Should have 4 chart canvases, found {len(charts)}"

    def test_chart_headings():
        bt = body_text(driver)
        assert "By Type" in bt,       "By Type chart heading should be visible"
        assert "By Severity" in bt,   "By Severity chart heading should be visible"
        assert "Monthly Trend" in bt, "Monthly Trend chart heading should be visible"
        assert "By Status" in bt,     "By Status chart heading should be visible"

    def test_filter_bar_present():
        assert "Filter" in body_text(driver), "Filter bar should be visible"

    def test_filter_by_type():
        select = wait_clickable(driver, By.CSS_SELECTOR, "select[name='type']")
        Select(select).select_by_visible_text("Phishing")
        driver.find_element(By.CSS_SELECTOR, "button.btn-filter").click()
        time.sleep(2)
        assert "Phishing" in body_text(driver), \
            "Filtered results should show Phishing"

    def test_clear_filter():
        driver.find_element(By.LINK_TEXT, "Clear").click()
        time.sleep(1.5)
        assert "Incident Records" in body_text(driver), \
            "After clearing filter, all records should show"

    def test_filter_by_severity():
        select = wait_clickable(driver, By.CSS_SELECTOR, "select[name='severity']")
        Select(select).select_by_visible_text("Critical")
        driver.find_element(By.CSS_SELECTOR, "button.btn-filter").click()
        time.sleep(2)
        assert "Critical" in body_text(driver), \
            "Filtered results should show Critical incidents"
        driver.find_element(By.LINK_TEXT, "Clear").click()
        time.sleep(1.5)

    def test_incidents_table():
        bt = body_text(driver)
        assert "Incident Records" in bt, "Incidents table heading should be visible"
        assert "INC-" in bt, "Incident IDs should be in table"

    def test_click_row_expands():
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr[onclick]")
        assert len(rows) > 0, "Clickable incident rows should exist"
        driver.execute_script("arguments[0].scrollIntoView(true);", rows[0])
        driver.execute_script("arguments[0].click();", rows[0])
        time.sleep(1)
        detail_rows = driver.find_elements(By.CLASS_NAME, "detail-row")
        visible = [r for r in detail_rows if r.is_displayed()]
        assert len(visible) > 0, "Detail panel should expand when row clicked"

    def test_detail_panel_content():
        detail_rows = driver.find_elements(By.CLASS_NAME, "detail-row")
        visible = [r for r in detail_rows if r.is_displayed()]
        if visible:
            pt = visible[0].text
            assert any(f in pt for f in ["Incident ID","Type","Severity","Status","Occurred"]), \
                "Detail panel should show incident field labels"

    def test_detail_has_description():
        detail_rows = driver.find_elements(By.CLASS_NAME, "detail-row")
        visible = [r for r in detail_rows if r.is_displayed()]
        if visible:
            assert "Incident Description" in visible[0].text, \
                "Detail panel should have description section"

    def test_detail_has_investigation():
        detail_rows = driver.find_elements(By.CLASS_NAME, "detail-row")
        visible = [r for r in detail_rows if r.is_displayed()]
        if visible:
            assert "Investigation" in visible[0].text, \
                "Detail panel should have investigation section"

    def test_no_modify_buttons():
        classify = driver.find_elements(By.XPATH, "//button[contains(.,'Classify')]")
        assign   = driver.find_elements(By.XPATH, "//button[contains(.,'Assign')]")
        assert len(classify) == 0, "Management should not see Classify buttons"
        assert len(assign) == 0,   "Management should not see Assign buttons"

    def test_management_logout():
        logout(driver)
        assert "/management" not in driver.current_url, "Should be logged out"

    test("Management dashboard loads",               test_dashboard_loads)
    test("Read-only notice visible",                 test_readonly_notice)
    test("Stat cards visible",                       test_stat_cards_visible)
    test("Stat cards show numbers",                  test_stat_cards_have_numbers)
    test("All 4 chart canvases present",             test_four_charts_present)
    test("All 4 chart headings visible",             test_chart_headings)
    test("Filter bar present",                       test_filter_bar_present)
    test("Filter by type works",                     test_filter_by_type)
    test("Clear filter works",                       test_clear_filter)
    test("Filter by severity works",                 test_filter_by_severity)
    test("Incidents table loads with INC- IDs",     test_incidents_table)
    test("Click row expands detail panel",           test_click_row_expands)
    test("Detail panel shows incident fields",       test_detail_panel_content)
    test("Detail panel shows description",           test_detail_has_description)
    test("Detail panel shows investigation section", test_detail_has_investigation)
    test("Management has no modify buttons",         test_no_modify_buttons)
    test("Management logout",                        test_management_logout)

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("\n" + "═"*55)
    print("  CYBER INCIDENT MIS — SELENIUM TEST SUITE")
    print("  Make sure app.py is running on localhost:5000")
    print("═"*55)

    driver = None
    try:
        print("\n  Starting browser...")
        driver = get_driver()
        driver.get(BASE_URL)
        time.sleep(1.5)

        if "MIS" not in driver.title and "Cyber" not in body_text(driver):
            print("\n  ERROR: Could not reach app at localhost:5000")
            print("  Run: python app.py first")
            sys.exit(1)

        print("  Browser started. Running tests...\n")

        run_auth_tests(driver)
        run_reporter_tests(driver)
        run_analyst_tests(driver)
        run_admin_tests(driver)
        run_management_tests(driver)

    except Exception as e:
        print(f"\n  FATAL ERROR: {e}")
    finally:
        summary()
        if driver:
            time.sleep(2)
            driver.quit()
            print("  Browser closed.\n")

if __name__ == "__main__":
    main()