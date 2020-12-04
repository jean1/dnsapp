
Sémantique des droits :

Il y a 3 flags de permission : "r", "w" et "c"

* Permission sur les namespaces

Un namespace est géré par les admins de l'application.
La permission "r" pour un namespace pour un groupe signifie que
ce groupe peut voir ce namespace.
La permission "w" pour un namespace n'est pas utilisé.
La permission "c" pour un namespace pour un groupe signifie que
ce groupe peut créer des zones dans ce namespace.

Exemples : il n'existe pas de permission "c" sur le namespace "default" ; seuls
les admin y créent des zones.
Il y a une permission "c" pour le namespace "projetstar" pour le groupe "observatoire"
Ça signifie que les membre de ce groupe peuvent y créer des zones.
Les zones crées sont automatiquement modifiables et supprimables pour les groupes
(permission "rw")

* Permission sur les zones

La permission "r" pour une zone pour un groupe signifie que
ce groupe peut voir cette zone.
La permission "r" ne permet *pas* de voir les enregistrements 
de cette zone.
La permission "w" pour une zone pour un groupe signifie que :
  - ce groupe peut en modifier les attributs comme le serveur de nom et les autres paramètres du SOA.
  - ce groupe peut détruire la zone
La permission "w" ne dit rien sur la permission de modifier les RR qui font partie de la zone.
La permission "c" pour une zone pour un groupe signifie que ce groupe y créer des enregistrement

Exemples : il n'y a pas de permission "w" pour la zone "u-strasbg.fr" pour aucun groupe; seuls
les admin peuvent modifier ou supprimer la zone
il y a une permission "w" pour la zone "icube.unistra.fr" pour le groupe "icube" ; ce groupe
peut modifier le serveur de nom par exemple ou supprimer la zone.
Dans les 2 cas, il y a une permission "c" pour le groupe "icube", ce qui lui permet
de créer des enregistrements dans les 2 zones.

* Permission sur les RR

La permission "r" pour une rr pour un groupe signifie que
ce groupe peut voir cet enregistrement.
La permission "w" pour une rr pour un groupe signifie que
ce groupe peut modifier et supprimer cet enregistrement.

* Mise en place des droits 

Les permissions sont mises en place à la création
d'un objets zone et RR.
La permission est créé avec le mécanisme suivant :
- d'abord on regarde si une préférence pour la zone et l'utilisateur
existe, et si elle existe, on crée la permission pour le
groupe trouvé pour l'objet créé.
- si on ne trouve pas de préférence, un crée une permission
"rw" avec le groupe indiqué dans l'attribut "default_pref"
de l'utilisateur (NB : default_pref est obligatoirement
renseigné pour chaque utilisateur)

* Autres vérifications

FIXME
