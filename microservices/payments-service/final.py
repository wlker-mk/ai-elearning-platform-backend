#!/usr/bin/env python3
"""
Correction finale de Payment.java
Supprime les méthodes UnsupportedOperationException
"""

from pathlib import Path

def fix_payment_entity():
    """Corriger Payment.java - Supprimer les méthodes problématiques"""
    
    payment_file = Path("src/main/java/com/lms/payment/model/entity/Payment.java")
    
    if not payment_file.exists():
        print(f"❌ Fichier non trouvé: {payment_file}")
        return False
    
    print("🔧 Correction de Payment.java...")
    content = payment_file.read_text(encoding='utf-8')
    
    # Supprimer les 2 méthodes problématiques
    lines_to_remove = [
        "    public void setStatus(PaymentStatus paymentStatus) {",
        '        throw new UnsupportedOperationException("Not supported yet.");',
        "    }",
        "",
        "    public void setExternalReference(String pi_test123) {",
        '        throw new UnsupportedOperationException("Not supported yet.");',
        "    }",
    ]
    
    # Méthode plus robuste: chercher et supprimer le bloc entier
    lines = content.split('\n')
    new_lines = []
    skip_until = -1
    
    for i, line in enumerate(lines):
        # Si on est dans une zone à skip
        if i < skip_until:
            continue
        
        # Détecter le début d'une méthode UnsupportedOperationException
        if 'public void set' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            if 'UnsupportedOperationException' in next_line:
                # Trouver la fin de la méthode (le prochain })
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == '}':
                        skip_until = j + 1
                        print(f"  ✓ Supprimé: {line.strip()}")
                        break
                continue
        
        new_lines.append(line)
    
    # Réécrire le fichier
    new_content = '\n'.join(new_lines)
    payment_file.write_text(new_content, encoding='utf-8')
    
    # Vérification
    if 'UnsupportedOperationException' not in new_content:
        print("✅ Payment.java corrigé avec succès!")
        return True
    else:
        print("⚠️  Des méthodes UnsupportedOperationException restent")
        return False

if __name__ == "__main__":
    print("="*70)
    print("  🔧 CORRECTION FINALE - Payment.java")
    print("="*70)
    fix_payment_entity()
    print("="*70)