# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Congressman, Discourse, Proposition, PropositionTag, Vote


@admin.register(Congressman)
class CongressmanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'condition',
        'party',
        'state',
        'gender',
        'birth_city',
        'birth_state',
        'birh_date',
        'scholarity',
        'created_at',
        'modified_at',
    )
    list_filter = ('state', 'party', 'condition', 'gender', 'scholarity')
    search_fields = ('name', 'state', 'party', 'condition', 'gender', 'scholarity')


@admin.register(Discourse)
class DiscourseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'congressman',
        'session',
        'phase',
        # 'summary',
        'pronounced_at',
    )
    list_filter = ('pronounced_at', 'congressman__party', 'congressman__state')
    raw_id_fields = ('congressman',)
    date_hierarchy = 'pronounced_at'


@admin.register(Proposition)
class PropositionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'subject',
        'type_name',
        'type_code',
        'number',
        'year',
        'numberer_code',
        'proposed_at',
    )
    list_filter = ('congressmen__party', 'congressmen__state', 'type_code',)
    search_fields = ('name', 'congressmen__name', 'congressmen__party', 'congressmen__scholarity', 'subject', 'summary')
    date_hierarchy = 'proposed_at'


@admin.register(PropositionTag)
class PropositionTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'count_propositions')
    list_filter = ('created_at', 'modified_at')
    date_hierarchy = 'created_at'

    def count_propositions(self, obj):
        return obj.propositions.count()

    count_propositions.short_description = '# Propositions'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        'congressman',
        'proposition',
        'session_code',
        'vote',
        'presence',
        'absence_reason',
    )
    list_filter = (
        'congressman__party',
        'congressman__state',
        'proposition__type_code',
    )
    date_hierarchy = 'session_date'
