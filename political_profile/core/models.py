from django.db import models

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Congressman(models.Model):
    # Basic
    id = models.IntegerField('id', primary_key=True)
    author_id = models.IntegerField('author id', unique=True)
    matriculation_id = models.IntegerField('matriculation id', null=True)
    budget_id = models.IntegerField('budget id', null=True)
    registration_id = models.IntegerField('registration id', null=True)
    condition = models.CharField('condition', max_length=255, null=True)
    profile_url = models.URLField('url_field', null=True)
    name = models.CharField('name', max_length=255, null=True)
    party = models.CharField('party', max_length=255, null=True)
    state = models.CharField('state', max_length=255, null=True)
    mandate_id = models.IntegerField('mandate it', null=True)
    photo_url = models.URLField('photo url', null=True)

    # Detailed
    gender = models.CharField('gender', max_length=255, null=True)
    legal_name = models.CharField('legal name', max_length=255, null=True)
    phone_number = models.CharField('phone #', max_length=255, null=True)
    email = models.EmailField('email', null=True)

    cpf = models.CharField('cpf', max_length=255, null=True)
    birth_city = models.CharField('birth city', max_length=255, null=True)
    birth_state = models.CharField('birth state', max_length=255, null=True)
    birh_date = models.DateField('birth date', null=True)

    scholarity = models.CharField('scholarity', max_length=255, null=True)

    created_at = models.DateTimeField('created at', auto_now_add=True)
    modified_at = models.DateTimeField('modified at', auto_now=True)

    class Meta:
        verbose_name = 'Congressman'
        verbose_name_plural = 'Congressmen'
        ordering = 'name',

    def __str__(self):
        return self.name


class Discourse(models.Model):
    congressman = models.ForeignKey('Congressman', related_name='discourses', on_delete=models.CASCADE)
    session = models.CharField('session type', max_length=255)
    phase = models.CharField('phase', max_length=255)
    summary = models.TextField('summary')

    pronounced_at = models.DateTimeField('when')
    created_at = models.DateTimeField('created at', auto_now_add=True)
    modified_at = models.DateTimeField('modified at', auto_now=True)

    class Meta:
        verbose_name = 'Discourse'
        verbose_name_plural = 'Discourses'
        ordering = 'congressman__name',

    def __str__(self):
        return '{} - {}'.format(self.congressman.name, self.pronounced_at.strftime(DATETIME_FORMAT))


class Proposition(models.Model):
    id = models.IntegerField('id', primary_key=True)
    congressmen = models.ManyToManyField('Congressman', related_name='propositions', blank=True)
    name = models.CharField('name', max_length=255, null=True)
    url = models.URLField('URL', null=True)
    file_url = models.URLField('file url', null=True)
    subject = models.CharField('subject', max_length=255, null=True)
    summary = models.TextField('summary', null=True)
    detailed_summary = models.TextField('detailed summary', null=True)
    status = models.TextField('status', null=True)
    type_code = models.CharField('type code', max_length=255, null=True)
    type_name = models.CharField('type name', max_length=255, null=True)
    numberer_code = models.CharField('numberer code', max_length=255, null=True)
    numberer_name = models.TextField('numberer name', null=True)
    number = models.CharField('number', max_length=255, null=True)
    year = models.IntegerField('year', null=True)
    full_content = models.TextField('full content', null=True)
    votes = models.ManyToManyField('Congressman', through='Vote', related_name='votes', blank=True)

    proposed_at = models.DateTimeField('started at', null=True)
    created_at = models.DateTimeField('created at', auto_now_add=True)
    modified_at = models.DateTimeField('modified at', auto_now=True)

    class Meta:
        verbose_name = 'Proposition'
        verbose_name_plural = 'Propositions'
        ordering = '-proposed_at',

    def __str__(self):
        return self.name


class PropositionTag(models.Model):
    propositions = models.ManyToManyField('Proposition', related_name='tags', blank=True)
    tag = models.CharField('tag', max_length=255, unique=True)

    created_at = models.DateTimeField('created at', auto_now_add=True)
    modified_at = models.DateTimeField('modified at', auto_now=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = 'tag',

    def __str__(self):
        return self.tag


class Vote(models.Model):
    congressman = models.ForeignKey('Congressman', on_delete=models.CASCADE)
    proposition = models.ForeignKey('Proposition', on_delete=models.CASCADE)

    session_code = models.CharField('session code', max_length=255)
    session_date = models.DateField('session date')

    vote = models.CharField('vote', max_length=255, null=True)

    presence = models.CharField('presence', max_length=255)
    absence_reason = models.CharField('absence reason', max_length=255, null=True)

    created_at = models.DateTimeField('created at', auto_now_add=True)

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        ordering = '-session_date', 'session_code'
        unique_together = 'congressman', 'proposition', 'session_date'

    def __str__(self):
        return self.vote


# Graveyard

# class Session(models.Model):
#     name = models.CharField('name', max_length=255)
#     date = models.DateField('date')
#
#     created_at = models.DateTimeField('created at', auto_now_add=True)
#     modified_at = models.DateTimeField('modified at', auto_now=True)
#
#     class Meta:
#         verbose_name = 'Session'
#         verbose_name_plural = 'Sessions'
#         ordering = 'date', 'name'
#
#     def __str__(self):
#         return self.name
