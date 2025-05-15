import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FORM_URL = "" #your googleform ling

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless=new")  # Розкоментуйте після тестування

FIXED_ANSWERS = {
    
}

class FormFiller:
    def __init__(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 20)

    def open_form(self):
        self.driver.get(FORM_URL)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="listitem"]')))
        time.sleep(2)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
        time.sleep(0.5)

    def get_question_text(self, question_element):
        try:
            return question_element.find_element(By.CSS_SELECTOR, '.M7eMe').text.strip()
        except:
            return ""

    def answer_fixed_question(self, question_element, possible_answers):
        try:
            choices = question_element.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
            for choice in choices:
                choice_text = choice.text.strip()
                for answer in possible_answers:
                    if choice_text.startswith(answer.split(')')[0] + ")"):
                        self.scroll_to_element(choice)
                        choice.click()
                        print(f"✅ Вибрано: {answer}")
                        time.sleep(0.5)
                        return True
            return False
        except Exception as e:
            print(f"❌ Помилка: {str(e)}")
            return False

    def answer_random_question(self, question_element):
        try:
            # Радіо-кнопки
            radio_buttons = question_element.find_elements(By.CSS_SELECTOR, 'div[role="radio"]')
            if radio_buttons:
                choice = random.choice([rb for rb in radio_buttons if rb.is_displayed()])
                self.scroll_to_element(choice)
                choice.click()
                print(f"🔘 Випадково: {choice.text[:30]}...")
                time.sleep(0.3)
                return True

            # Чекбокси
            checkboxes = question_element.find_elements(By.CSS_SELECTOR, 'div[role="checkbox"]')
            if checkboxes:
                for cb in random.sample([c for c in checkboxes if c.is_displayed()], min(2, len(checkboxes))):
                    self.scroll_to_element(cb)
                    cb.click()
                    print(f"☑️ Випадково: {cb.text[:30]}...")
                    time.sleep(0.3)
                return True

            # Текстові поля
            text_inputs = question_element.find_elements(By.CSS_SELECTOR, 'textarea, input[type="text"]')
            if text_inputs:
                for field in text_inputs:
                    if field.is_displayed():
                        self.scroll_to_element(field)
                        field.send_keys("Відповідь")
                        print("📝 Введено текст")
                        time.sleep(0.5)
                return True

            return False
        except Exception as e:
            print(f"❌ Помилка: {str(e)}")
            return False

    def answer_question(self, question_element):
        question_text = self.get_question_text(question_element)
        if not question_text:
            return False

        print(f"\n🔍 Питання: {question_text[:80]}...")

        for pattern, answers in FIXED_ANSWERS.items():
            if pattern in question_text:
                print("🎯 Фіксоване питання")
                if self.answer_fixed_question(question_element, answers):
                    return True
                break

        return self.answer_random_question(question_element)

    def submit_form(self):
        try:
            # Очікуємо і прокручуємо до кнопки
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button"]//*[contains(text(), "Надіслати") or contains(text(), "Submit")]'))
            )
            self.scroll_to_element(submit_button)
            time.sleep(1)
            
            # Використовуємо JavaScript для надійного кліку
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("✅ Надіслання форми (JS click)")
            time.sleep(3)
            
            # Перевіряємо підтвердження
            if "formResponse" in self.driver.current_url:
                print("🎉 Форму успішно відправлено!")
                return True
            return False
        except Exception as e:
            print(f"❌ Помилка при відправці: {str(e)}")
            return False

    def fill_form(self):
        try:
            self.open_form()
            questions = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="listitem"]')
            
            for question in questions:
                self.answer_question(question)
            
            # Додаткова пауза перед відправкою
            time.sleep(2)
            return self.submit_form()
        except Exception as e:
            print(f"❌ Помилка: {str(e)}")
            return False
        finally:
            time.sleep(2)
            self.driver.quit()

def main():
    for i in range(25):
        print(f"\n=== Форма {i+1}/ ===")
        start_time = time.time()
        
        filler = FormFiller()
        if filler.fill_form():
            print(f"✅ Успішно ({time.time()-start_time:.1f} сек)")
        else:
            print(f"⚠️ Помилка ({time.time()-start_time:.1f} сек)")
        
        if i < 3:
            pause = random.uniform(3, 7)
            print(f"⏳ Пауза {pause:.1f} сек...")
            time.sleep(pause)

    print("\n🎉 Всі форми оброблено!")

if __name__ == "__main__":
    main()