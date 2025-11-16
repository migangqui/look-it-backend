# Instrucciones para realizar commit y push en Git

1. **Ir a la ruta del proyecto:**
   
   ```bash
   cd "/Users/mangelquintanilla/Documents/DEV/MIO/CURSO IA/PROYECTO/look-it/look-it-backend"
   ```

2. **Verificar y ejecutar el comando para añadir archivos:**
   
   ```bash
   cd "/Users/mangelquintanilla/Documents/DEV/MIO/CURSO IA/PROYECTO/look-it/look-it-backend" & git add .
   ```
   
   *Este comando añade todos los archivos modificados al área de preparación (staging). Verifica que el comando es correcto antes de ejecutarlo.*

3. **Verificar y ejecutar el comando para hacer commit:**
   
   ```bash
   git commit -m "COMMIT_MESSAGE"
   ```
   
    *Reemplaza `COMMIT_MESSAGE` por el mensaje generado automáticamente según los cambios detectados en los archivos. El mensaje de commit debe estar **siempre en idioma inglés**. Verifica el mensaje antes de ejecutar el comando.*

4. **Verificar y ejecutar el comando para hacer push:**
   
   ```bash
   git push origin BRANCH
   ```
   
   *Reemplaza `BRANCH` por el nombre de la rama actual. Verifica el nombre de la rama antes de ejecutar el comando.*


**Nota:** Antes de ejecutar cada comando, muéstralo en la terminal para verificar que es el correcto.