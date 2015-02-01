
Wyświetlanie stron internetowych
================================

Wejście pod główny adres http://localhost:8000/ nadal powoduje wyświetlenie brzydkiej strony błędu. Nie może tak dalej
być!

Dobrze jest zacząć pracę nad nowym serwisem internetowym od przemyślenia struktury URLi (adresów). Wiemy, że będziemy
chcieli wyświetlić listę wszystkich ankiet na stronie, pozwolić użytkownikom zagłosować oraz wyświetlić zbiorcze wyniki
ankiety.

Jeszcze raz otwórzmy plik ``urls.py`` i dodajmy cztery nowe wpisy. Ostatecznie plik powinien wyglądać następująco::

  from django.conf.urls import patterns, include, url

  from django.contrib import admin
  admin.autodiscover()

  urlpatterns = patterns('',
      url(r'^polls/$', 'polls.views.index'),
      url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
      url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
      url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
      url(r'^admin/', include(admin.site.urls)),
  )

Przyjrzyjmy się temu przykładowi raz jeszcze. Każdy argument przekazany do funkcji ``patterns`` (poza pierwszym, ale
o tym potem) określa nam wzorzec URL (adresu). Wzorzec ten zapisany jest za pomocą
`wyrażenia regularnego <http://pl.wikipedia.org/wiki/Wyra%C5%BCenie_regularne#Wyra.C5.BCenia_regularne_w_praktyce>`_.
Jest to trudne techniczne określenie malutkiego języka, służącego do zwięzłej reprezentacji wzorców tekstu.

Kiedy użytkownik próbuje wejść na określony adres na naszej stronie, taki jak http://localhost:8000/polls/1/,
Django wybiera część URL po trzecim ukośniku (w tym przypadku ``polls/1/``)  i próbuje ją kolejno dopasować do wyrażeń
regularnych z ``urlpatterns``. Przyjrzyjmy się przykładowi takiego wyrażenia::

   r'^polls/(?P<poll_id>\d+)/vote/$'

Tak naprawdę jest to normalny ciąg znaków (może poza poczatkowym ``r``, które jest tu używane tylko dla wygody).
Kiedy próbujemy do niego dopasować tekst (nadal myślimy o ``polls/1/``), musimy pamietać o następujacych zasadach:

.. admonition:: Wyrażenia regularne
   :class: alert alert-info

   * Każda litera i cyfra wyrażenia regularnego pasuje tylko do takiej samej litery/cyfry ciągu dopasowywanego. Tak samo
     ukośnik (``/``), spacja, podkreślenie (``_``) i myślnik (``-``).

   * ``^`` pasuje tylko do początku ciągu znaków (nie do znaku, "początek" należy tutaj traktować jak abstrakcyjny twór
     przed pierwszym znakiem).

   * ``$`` pasuje tylko do końca ciągu znaków (na podobnej zasadzie co "początek").

   * Kropka (``.``) pasuje do dowolnego znaku.

   * Jeżeli kilka znaków obejmiemy nawiasami kwadratowymi, np. tak ``[aBde]``, taka grupa liczy się jako jedna całość i
     dopasuje się do dowolnego jednego znaku z wewnątrz grupy.

   * Istnieje skrótowa notacja dla takich grup. Zamiast wypisywać wszystkie małe litery alfabetu, możemy napisac ``[a-z]``,
     aby dopasować dowolną jedną małą literę. Tak samo dla dużych liter ``[A-Z]`` lub cyfr ``[0-9]``.

   * Dopasować jedną cyfrę można jeszcze krócej, używając znaczka ``\d``.

   * Jeżeli po dowolnym z powyższych wyrażeń postawimy znak ``?``, zostanie ono potraktowane jako *opcjonalne*. Oznacza
     to, że jeżeli w ciągu dopasowywanym nie będzie takiego wyrażenia, nadal będzie możliwe jego dopasowanie. Jeżeli
     będzie, zostanie dopasowane.

   * Jeżeli po wyrażeniu postawimy znak ``*``, dopasuje się ono z dowolną ilością powtorzeń wyrażenia (wliczając w to zero
     powtórzeń, czyli tak jakby było *opcjonalne*).

   * Jeżeli po wyrażeniu postawimy znak ``+``, dopasuje się ono z dowolną ilością powtórzeń wyrażenia, z wyjątkiem zera
     powtórzeń (tzn. wyrażenie musi wystąpić co najmniej raz).

   * Jeżeli kilka znaków obejmiemy nawiasami zwykłymi, np. tak ``(\d\d)``, zostaną one potraktowane jako grupa i wszystkie
     powyższe modyfikatory będą na nie działały w całości. Jeżeli dodatkowo napiszemy to z ``(?P<NAZWA>napis)``, grupa
     zostanie nazwana i będzie się do niej można potem odwołać pod nazwą ``NAZWA``. Jest to bardzo popularne przy pracy w
     Django.

Uff... Jest jeszcze wiele reguł, ale tak naprawdę nikt ich wszystkich nie pamięta. Te powyższe wystarczają w większości
przypadków.

Czy widzisz już, że przykładowe wyrażenie dopasuje się do ``polls/1/``? Dlaczego?

Kiedy już Django znajdzie dopasowanie, popatrzy na drugą część linii. Określa ona widok, który ma być wywołany w celu
utworzenia strony dla użytkownika. Dla ``polls/1/`` będzie to ``polls.views.detail``. Wszystkie nazwane grupy zostaną
przekazane widokowi jako argumenty o tej samej nazwie.

Pierwszy widok
--------------

Dobra, zobaczmy, jak to działa w praktyce. Niestety, wejście pod adres http://localhost:8000/polls/1/ nie kończy się
dobrze::

  ViewDoesNotExist at /polls/1/

  Could not import polls.views.detail. View does not exist in module polls.views.

Ach, to dlatego, że nie zdefiniowaliśmy jeszcze widoku (Django podpowiada nam, że szukało ``polls.views.detail``,
niestety bez powodzenia)!

Popraw plik ``polls/views.py``, aby wyglądał następująco::

    from django.http import HttpResponse

    def index(request):
        return HttpResponse("Hello, world. You're at the poll index.")

    def detail(request, poll_id):
        return HttpResponse("You're looking at poll %s." % poll_id)

    def results(request, poll_id):
        return HttpResponse("You're looking at the results of poll %s." % poll_id)

    def vote(request, poll_id):
        return HttpResponse("You're voting on poll %s." % poll_id)

Tak wygladają najprostsze możliwe widoki. Nie zwracają one zwykłych ciagów znaków, tak jak funkcja budująca choinkę w
Pythonie, bo muszą mówić protokołem HTTP, który jest nieco bardziej skomplikowany (tutaj dobrze byłoby zobaczyć w
przeglądarce co się tak naprawde dzieje, gdy wchodzimy pod adres http://localhost:8000/polls/1/).


Widok, który naprawdę coś robi
------------------------------

Nasze widoki na razie nie robią zbyt wiele. Dajmy im trochę popracować!

Wszystko, czego Django potrzebuje od widoku, to obiekt :class:`django.http.HttpResponse`
lub wyrzucenie wyjątku. Cała reszta jest pod naszą kontrolą. Możemy na przykład użyć funkcji, które poznaliśmy w trybie
interaktywnym, aby wyświetlić wszystkie ankiety użytkownikowi.

Dopisz na początek pliku ``polls/views.py``::

    from django.http import HttpResponse
    from polls.models import Poll

Rozbuduj funkcję :func:`index` aby wyglądała następująco:

.. code-block:: python

  def index(request):
      latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
      output = ', '.join([p.question for p in latest_poll_list])
      return HttpResponse(output)

.. note::

    Teraz nie podajemy już całej treści pliku, bo byłaby ona za długa. Podawane są tylko najważniejsze zmiany.

Działa! Jest tylko jeden problem z tym przykładem: określamy w widoku nie tylko
to, co ma być zwrócone, ale też w jakim formacie ma zostać zwrócone
użytkownikowi serwisu. Jedną z najważniejszych umiejętności programisty jest
zdolność do odróżnienia i rozdzielenia dwóch niezależnych rzeczy: danych oraz wyglądu.
Programiści Django o tym pomyśleli i stworzyli system szablonow:

Dopisz na początek pliku ``polls/views.py``::

  from django.template import Context, loader

To pozwoli nam używać systemu szablonów.

Rozbuduj funkcję :func:`index` w tym samym pliku aby wyglądała następująco::

  def index(request):
      latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
      t = loader.get_template('polls/index.html')
      c = Context({
          'latest_poll_list': latest_poll_list,
      })
      return HttpResponse(t.render(c))

Za obsługę szablonu w tym wypadku są odpowiedzialne funkcje :func:`~django.template.loader.get_template`
(Znajduje szablon) oraz :meth:`~django.template.render` (zmienia szablon na test, który dostanie ostatecznie użytkownik).

Kod jest trochę dłuższy, ale zaraz zobaczymy, o ile bardziej wszystko będzie czytelne. Najpierw załadujmy jednak stronę
http://localhost:8000/polls/, aby zobaczyć wynik naszej pracy::

   TemplateDoesNotExist at /polls/
   polls/index.html

Ups! No tak, nie dodaliśmy jeszcze szablonu. Aby to zrobić, stwórzmy plik ``polls/templates/polls/index.html`` i dodajmy
do niego:

.. code-block:: django

   {% if latest_poll_list %}
   <ul>
       {% for poll in latest_poll_list %}
           <li><a href="/polls/{{ poll.id }}/">{{ poll.question }}</a></li>
       {% endfor %}
   </ul>
   {% else %}
       <p>No polls are available.</p>
   {% endif %}

.. note::

    Szablony aplikacji znajdują się w katalogu ``templates`` aplikacji, a funkcja :func:`~django.template.loader.get_template`
    sama szuka szablonów w tych katalogach, dlatego nie musieliśmy podawać całej ścieżki
    ``polls/templates/polls/index.html``, wystarczyło ``polls/index.html``.

Po przeładowaniu strony w przeglądarce powinniśmy zobaczyć listę zawierającą wszystkie utworzone wcześniej ankiety.

.. note::

    Jeżeli po odświeżeniu strony nadal widać błąd, należy ponownie uruchomić serwer. W konsoli, w której już jest
    uruchomiony serwer, wciskamy ``Ctrl+C`` i wykonujemy ``python manage.py runserver`` ponownie.
    Teraz powinno już działać.

.. note::

   HTML i CSS sa formatami służącymi do określania wyglądu stron internetowych. Szablonów Django będziemy używać po to,
   aby generować kod HTML. Dobry opis HTML znajduje się w książce
   `Interactive Data Visualization for the Web <http://ofps.oreilly.com/titles/9781449339739/k_00000003.html>`_.
   Zachwycającą własnością sieci WWW jest to, że kody HTML i CSS każdej strony są zupełnie jawne. Polecam obejrzenie kodu
   ulubionych stron.

Prawie w każdym widoku będziemy chcieli ostatecznie użyć szablonu. Dlatego w Django jest funkcja :func:`django.shortcuts.render`,
która pozwala zrobić to w krótszy sposób.

Popraw początek pliku ``polls/views.py``, aby wyglądał następująco::

  from django.shortcuts import render
  from polls.models import Poll

Popraw funkcję :func:`index`, aby wyglądała następująco::

  def index(request):
      latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
      return render(
          request,
          'polls/index.html',
          {'latest_poll_list': latest_poll_list})


Zwracanie 404
-------------

Zajmijmy się teraz widokiem szczegółow ankiety -- strony, która wyświetla pytania z konkretnej ankiety.

Dopisz na początku pliku ``polls/views``::

    from django.http import Http404

``Http404`` to wyjątek udostępniony przez Django. W sytuacji, gdy nasza aplikacja nie potrafi odnaleźć
żądanej przez użytkownika ankiety, możemy rzucić ten wyjątek (przez napisanie ``raise Http404``). Efektem
tego będzie wyświetlenie strony błędu 404 w przeglądarce.

.. note::

   Można zmienić stronę wyswietlaną przez Django w wypadku błędu 404 (brak strony) i 500 (nieoczekiwany błąd serwera).
   W tym celu trzeba stworzyć szablony ``404.html`` i ``500.html``. Przed sprawdzeniem, czy to zadziałało, należy zmienić
   :django:setting:`DEBUG` w pliku ``settings.py`` na ``False``, inaczej Django nadal będzie wyświetlać swoje pomocnicze
   *żółte* strony.

Popraw funkcję :func:`detail` aby wyglądała następująco::

    def detail(request, poll_id):
        try:
            p = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            raise Http404
        return render(request, 'polls/detail.html', {'poll': p})

Następnie stwórz plik ``polls/templates/polls/detail.html`` o następującej treści:

.. code-block:: django

    <h1>{{ poll.question }}</h1>
    <ul>
    {% for choice in poll.choice_set.all %}
        <li>{{ choice.choice_text }}</li>
    {% endfor %}
    </ul>


Obsługa formularzy
------------------

Zmieńmy szablon ``polls/templates/polls/details.html``, dodając tam prosty formularz HTML.

Popraw plik ``polls/templates/polls/details.html``, aby wyglądał następująco:

.. code-block:: django

  <h1>{{ poll.question }}</h1>

  {% if error_message %}<p><strong>{{ error_message }}</strong></p>{% endif %}

  <form action="/polls/{{ poll.id }}/vote/" method="post">
  {% csrf_token %}
  {% for choice in poll.choice_set.all %}
      <input type="radio" name="choice" id="choice{{ forloop.counter }}" value="{{ choice.id }}" />
      <label for="choice{{ forloop.counter }}">{{ choice.choice_text }}</label><br />
  {% endfor %}
  <input type="submit" value="Vote" />
  </form>

.. note::

   Tag :django:templatetag:`{% csrf_token %} <django:csrf_token>` zabezpiecza nasz formularz przed `atakiem
   typu Cross-Site Request Forgery <https://www.owasp.org/index.php/Top_10_2013-A8-Cross-Site_Request_Forgery_%28CSRF%29>`_.
   Więcej na temat zabezpieczeń przeciwko CSRF w Django można znaleźć :mod:`tutaj <django:django.middleware.csrf>`.

Uważny czytelnik zauważy, że formularz wysyłany jest na adres ``/polls/{{ poll.id }}/vote/``, który nie obsługuje
jeszcze danych formularza. Dodamy teraz obsługę formularzy.

Na początku pliku ``polls/views.py`` dopisz::

    from django.http import HttpResponseRedirect
    from django.core.urlresolvers import reverse
    from django.shortcuts import get_object_or_404
    from polls.models import Choice

Popraw funkcję :func:`vote`, aby wyglądała następująco::

    def vote(request, poll_id):
        p = get_object_or_404(Poll, id=poll_id)
        try:
            selected_choice = p.choice_set.get(id=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Wyświetl błąd użytkownikowi, gdy wybrał złą opcję
            return render(request, 'polls/detail.html', {
                'poll': p,
                'error_message': "Musisz wybrać poprawną opcję.",
            })

        # Zapisz nową liczbę głosów
        selected_choice.votes += 1
        selected_choice.save()
        # Przekieruj użytkownika do widoku detali ankiety, na którą właśnie zagłosował
        return HttpResponseRedirect(reverse('polls.views.results', args=(p.id,)))

W tym widoku pojawia się sporo nowych koncepcji, o których nie mówiliśmy.

Obiekt :class:`request <django:django.http.HttpRequest>` zawiera dane wysłane
przez użytkownika, a :attr:`request.POST <django:django.http.HttpRequest.POST>` zawiera dane z formularza
wysłanego przez użytkownika. W ten sposób wiemy, która opcja została wybrana.

Tutaj pojawia się ważna kwestia. Może okazać się, że widok dostał nieistniejącą odpowiedź.
Zawsze musimy sprawdzać dane otrzymane od użytkownika i reagować, jeśli te dane są bezsensowne.
To właśnie dzieje się po :keyword:`except`. Odsyłamy wtedy użytkownika do ankiety i wyświetlamy błąd.

Jeżeli użytkownik wybrał poprawną opcję, możemy zwiększyć liczbę głosów i zapisać zmiany.
Następnie wykonujemy przekierowanie za pomocą :class:`~django.http.HttpResponseRedirect` do wcześniej napisanego
widoku detali ankiety.

Kolejna istotna sprawa: po zagłosowaniu mogliśmy po prostu wyświetlić jakąś stronę, podobnie jak na końcu widoku detali
(za pomocą :func:`~django.shortcuts.render`). Niestety, mogłoby to prowadzić do ponownego wysłania ankiety, gdyby użytkownik
zaczął bawić się przyciskami "wstecz" i "dalej" w przeglądarce lub gdyby po prostu odświeżył stronę (np. klawiszem ``f5``).

W skrócie, zawsze po poprawnym wysłaniu formularza (w tym wypadku: zagłosowaniu na ankietę) powinniśmy wykonać
przekierowanie za pomocą :class:`~django.http.HttpResponseRedirect`.

Na koniec pozostał nam do opracowania widok wyników ankiety, wyświetlany po zagłosowaniu.

Popraw funkcję :func:`results`, aby wyglądała następująco::

  def results(request, poll_id):
      p = get_object_or_404(Poll, id=poll_id)
      return render(request, 'polls/results.html', {'poll': p})

Oraz stwórz plik ``polls/templates/polls/results.html``, o następującej treści:

.. code-block:: django

  <h1>{{ poll.question }}</h1>

  <ul>
  {% for choice in poll.choice_set.all %}
      <li>{{ choice.choice_text }} -- {{ choice.votes }} vote{{ choice.votes|pluralize }}</li>
  {% endfor %}
  </ul>

  <a href="/polls/{{ poll.id }}/">Vote again?</a>

To wszystko! Wejdź pod adres http://localhost:8000/admin/ i stwórz kilka nowych ankiet i pytań, a potem pobaw się,
głosując na nie i namawiając inne osoby, aby zrobiły to samo.


.. admonition:: ``polls/views.py``
   :class: alert alert-hidden

   .. code-block:: python

        from django.http import HttpResponseRedirect
        from django.core.urlresolvers import reverse
        from django.shortcuts import get_object_or_404

        from polls.models import Choice
        from django.http import Http404
        from django.shortcuts import render
        from polls.models import Poll


        def index(request):
            latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
            return render(
                request,
                'polls/index.html',
                {'latest_poll_list': latest_poll_list})


        def detail(request, poll_id):
            try:
                p = Poll.objects.get(id=poll_id)
            except Poll.DoesNotExist:
                raise Http404
            return render(request, 'polls/detail.html', {'poll': p})


        def results(request, poll_id):
            p = get_object_or_404(Poll, id=poll_id)
            return render(request, 'polls/results.html', {'poll': p})


        def vote(request, poll_id):
            p = get_object_or_404(Poll, id=poll_id)
            try:
                selected_choice = p.choice_set.get(id=request.POST['choice'])
            except (KeyError, Choice.DoesNotExist):
                # Wyświetl błąd użytkownikowi, gdy wybrał złą opcję
                return render(request, 'polls/detail.html', {
                    'poll': p,
                    'error_message': "Musisz wybrać poprawną opcję.",
                })

            # Zapisz nową liczbę głosów
            selected_choice.votes += 1
            selected_choice.save()
            # Przekieruj użytkownika do widoku detali ankiety, na którą właśnie zagłosował
            return HttpResponseRedirect(reverse('polls.views.results', args=(p.id,)))

.. admonition:: ``urls.py``
   :class: alert alert-hidden

   .. code-block:: python

        from django.conf.urls import patterns, include, url

        from django.contrib import admin
        admin.autodiscover()

        urlpatterns = patterns('',
          url(r'^polls/$', 'polls.views.index'),
          url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
          url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
          url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
          url(r'^admin/', include(admin.site.urls)),
        )

.. admonition:: ``polls/models.py``
   :class: alert alert-hidden

   .. code-block:: python

        from django.db import models

        class Poll(models.Model):
            question = models.CharField(max_length=200)
            pub_date = models.DateTimeField('date published')

            def __str__(self):
                return self.question


        class Choice(models.Model):
            poll = models.ForeignKey(Poll)
            choice_text = models.CharField(max_length=200)
            votes = models.IntegerField(default=0)

            def __str__(self):
                return self.choice_text
