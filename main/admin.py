from django.contrib import admin
from .models import Course, Block, SubBlock

class SubBlockInline(admin.StackedInline):
    model = SubBlock
    extra = 1
    fields = ('title', 'content', 'order')

class BlockInline(admin.StackedInline):
    model = Block
    extra = 1
    fields = ('title', 'content', 'order')
    inlines = [SubBlockInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')
    search_fields = ('title', 'description')
    inlines = [BlockInline]

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'content')
    inlines = [SubBlockInline]

@admin.register(SubBlock)
class SubBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'block', 'order')
    list_filter = ('block__course', 'block')
    search_fields = ('title', 'content')