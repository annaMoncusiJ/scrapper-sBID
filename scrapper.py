import chromedriver_autoinstaller
import csv
import json
import os
import sys

from config import *
from pantalla_carrega import LoadingScreen
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import messagebox
from threading import Thread


class ScrapperSBid:
    def __init__(self, password:str, search:str = "TARRAGONA", cercaPerCodiPostal:bool = False):
        chromedriver_autoinstaller.install()

        self.paginaCarrega = None

        loading_screen = LoadingScreen()  # Crear instancia de LoadingScreen
        loading_thread = Thread(target=self.show_loading_screen, args=(loading_screen,))
        loading_thread.start()        
        with open("form_data.json", "r") as json_file:
            data = json.load(json_file)
            self.username = data.get(0, data.get("username", ""))
            self.cycle_code = data.get(0, data.get("cycle_code", ""))
            hide_browser = data.get("hide_browser", False)

        self.password = password

        if hide_browser:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            self.driver = webdriver.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome()

        self.driver.implicitly_wait(10) # segundos
        self.wait = WebDriverWait(self.driver, 20, 1, TimeoutException)
        self.search = search
        self.cercaPerCodiPostal = False

        if(cercaPerCodiPostal):
            self.cercaPerCodiPostal = True
            

    def show_loading_screen(self, loading_screen):
        # Crea la pantalla de carga
        self.paginaCarrega = loading_screen
        self.paginaCarrega.show()


    def login(self):
        self.driver.get("https://www.empresaiformacio.org/sBid")

        self.coockiesButton()

        self.entraIframe(True)


        try:
            username_input = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='username']")))
            username_input.clear()
            username_input.send_keys(self.username)

            self.wait.until(EC.element_to_be_clickable((By.ID, "password"))).clear()
            self.wait.until(EC.element_to_be_clickable((By.ID, "password"))).send_keys(f"{self.password}\n")
                
            # Espera fins que l'enllaç "Entitat" sigui clicable i fes clic
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='menu_items']/li/a[contains(text(), 'Entitat')]"))).click()

        except TimeoutException:
            messagebox.showinfo("Error", "Usuari o contrasenya incorrectes")
            self.driver.quit()
            sys.exit()
            

        # Espera fins que l'enllaç "Cerca d'Entitats" sigui clicable i fes clic
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[@id='menu_items']/li/a[text()='Entitat']/following-sibling::ul/li/a[contains(text(), \"Cerca d'Entitats\")]"))).click()

        self.filtraEntitat()
        self.recorreEmpreses()

    def coockiesButton(self):
        self.entraIframe(True)

        try:
            cookies_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class = 'boto2']/button[@class = 'acceptar']")))
            if cookies_button:
                cookies_button.click()
        except TimeoutException:
            print("No hi ha boto de cookies")

    def entraIframe(self, desDeDefault:bool=False):
        if(desDeDefault):
            self.driver.switch_to.default_content()
            iframe = self.driver.find_element(By.ID, "jspContainer")

        else:   
            # Troba l'iframe que conté l'element del botó (pots inspeccionar la pàgina per trobar el nom o l'índex de l'iframe)
            iframe = self.driver.find_element(By.ID, "contentmain")

        # Canvia el context de Selenium cap a l'iframe
        self.driver.switch_to.frame(iframe)


    def recorreEmpreses(self):
        self.entraIframe(True)
        self.entraIframe()
        hiHaPaginaSeguent = True
        self.numPagines()
        while(hiHaPaginaSeguent):

            no_more_tables = self.wait.until(EC.presence_of_element_located((By.ID, "no-more-tables")))

            # Troba tots els elements div amb la classe "form-group" dins de l'element amb l'ID "no-more-tables"
            form_groups = no_more_tables.find_elements(By.CLASS_NAME, "form-group")

            longit = len(form_groups)

            # Recorre tots els form-groups i mostra el seu text
            for i in range(longit):
                
                dades = self.agafaDadesGenerals(i)
                
                dades.update(self.agafaDadesEmpresa())

                self.csv_writer.writerow([dades["empresa"], dades["codi"], dades["categoria"], dades["estat"], dades["correuElectronic"], dades["telefon"], dades["responsables"], dades["tutors"]])


            self.entraIframe(True)
            self.entraIframe()

            hiHaPaginaSeguent = self.seguentPagina()



    def agafaDadesGenerals(self, i):
        try:
            self.entraIframe(True)
            self.entraIframe()

            no_more_tables = self.wait.until(EC.presence_of_element_located((By.ID, "no-more-tables")))

            # Troba tots els elements div amb la classe "form-group" dins de l'element amb l'ID "no-more-tables"
            form_groups = no_more_tables.find_elements(By.CLASS_NAME, "form-group")
            tables = no_more_tables.find_elements(By.TAG_NAME, "table")

            form_group = form_groups[i]

            empresa = form_group.find_element(By.TAG_NAME, 'a').text

            taula = tables[i]
            
            codi = taula.find_element(By.XPATH, "tbody/tr/td[@data-title = 'CODI']/a")
            codiText = codi.text
            categoria = taula.find_element(By.XPATH, "tbody/tr/td[@data-title = 'CATEGORIA']").text

            codi.click()

            dades = {}
            dades["empresa"] = empresa
            dades["codi"] = codiText
            dades["categoria"] = categoria

            self.paginaCarrega.add_step()

            return dades
        except Exception as e:
            print("Error: " + str(e))
            sys.exit()
    
    def agafaDadesEmpresa(self):
        self.entraIframe(True)
        self.entraIframe()


        collapseEmpresa = self.wait.until(EC.presence_of_element_located((By.ID, 'collapseEmpresa')))
        estat = collapseEmpresa.find_element(By.XPATH, "//label[contains(text(),'Estat:')]/following-sibling::div/p").text

        dades = self.dadesContacte()
        dades["estat"] = estat

        dades.update(self.nomsUsuaris())

        self.entraIframe(True)
        
        returnLink = self.wait.until(EC.presence_of_element_located((By.XPATH, "//nav[@id = 'titleInfo']/a")))
        if(not ("Resultat Cerca" in returnLink.text)):
            self.driver.refresh()
            self.entraIframe(True)
            returnLink = self.wait.until(EC.presence_of_element_located((By.XPATH, "//nav[@id = 'titleInfo']/a")))



        returnLink.click()

        return dades
    

    def dadesContacte(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[text() = 'Dades de contacte']"))).click()

        dadesContacte = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id = 'dadesContacte']")))
        telefon = dadesContacte.find_elements(By.XPATH, "//label[contains(text(),'Telèfon:')]/following-sibling::div/p")[2].text
        correuElectronic = dadesContacte.find_element(By.XPATH, "//label[contains(text(),'Correu electrònic:')]/following-sibling::div/p").text

        dades = {}
        dades["telefon"] =  telefon
        dades["correuElectronic"] = correuElectronic

        return dades

    def nomsUsuaris(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Usuaris')]"))).click()

        usuaris = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id = 'ui-id-8']")))
        responsables = usuaris.find_element(By.XPATH, "//div[h4/a/label[contains(text(), 'Responsable CT')]]/following-sibling::div")
        responsables = responsables.find_elements(By.XPATH, "div/div")

        responsables = [responsable.find_element(By.TAG_NAME, "a").text for responsable in responsables]

        dades = {}
        dades["responsables"] = ";".join(responsables)

        tutors = usuaris.find_element(By.XPATH, "//div[h4/a/label[contains(text(), 'Tutor/a')]]/following-sibling::div")
        tutors = tutors.find_elements(By.XPATH, "div/div")

        tutors = [tutor.find_element(By.TAG_NAME, "a").text for tutor in tutors]

        dades["tutors"] = ";".join(tutors)

        return dades

    def seguentPagina(self):
        try:
            sguentPag = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id = 'no-more-tables']/nav/ul/li/a[span/text() = '»']")))

            if sguentPag:
                sguentPag.click()
        except TimeoutException:
            print("Ja no hi han més pagines")
            self.driver.close()
            self.paginaCarrega.close()

            return False
        
        return True
    
    def filtraEntitat(self):
        self.entraIframe(True)

        self.entraIframe()


        select_element = self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='cod_estudi_pk']")))

        # Crea un objecte Select a partir de l'element select
        select = Select(select_element)

        options = select.options

        #Busca l'opció que conte el codi del cicle
        for option in options:
            if self.cycle_code in option.text:
                option.click()
                break
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href = '#dadesEmpresa1']"))).click()

        if(self.cercaPerCodiPostal):
            codiPostal = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='dadesEmpresa1_2']/div/input[@type='text']")))
            codiPostal.clear()
            codiPostal.send_keys(self.search)
        else:
            municipi = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='dadesEmpresa1_2']/div/div/input[@type='text']")))

            municipi.clear()
            municipi.send_keys(self.search)

            self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//tbody/tr[1]"))).click()

        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='panel-footer']/span[@type = 'button'][@title = 'Cercar']"))).click()

    def csv_writer(self):
        with open("dadesEmpreses.csv", 'a+', newline='', encoding='utf-8') as csvfile:
            
            #Crea el csv
            self.csv_writer = csv.writer(csvfile)

            # Mou el cursor al principi del fitxer per a saber si el fitxer esta buit
            csvfile.seek(0)
            first_char = csvfile.read(1)
            if not first_char:

                self.csv_writer.writerow(['Empresa', 'Codi', 'Categoria', 'Estat', 'Correu electrònic', 'Telèfon', 'Responsables', 'Tutors'])


            self.login()
    

    def numPagines(self):
        numPag = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id = 'no-more-tables']/nav/ul/li[a/span/text() != '»'][a/span/text() != '«']")))
        numPag = len(numPag)/2
        maxLen = numPag*5

        self.paginaCarrega.set_max(maxLen)

