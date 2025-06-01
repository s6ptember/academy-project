from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Block, SubBlock
from orders.models import Order

def home(request):
    courses = Course.objects.all().order_by('id')[:3]
    return render(request, 'main/home.html', {'courses': courses})

def about(request):
    return render(request, 'main/about.html', {})

def reviews(request):
    return render(request, 'main/reviews.html', {})

def pricing(request):
    return render(request, 'main/pricing.html', {})

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'main/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not Order.objects.filter(user=request.user, course=course, status='completed').exists():
        return render(request, 'main/access_denied.html', {'course': course})
    
    first_block = course.blocks.order_by('order').first()
    first_subblock = first_block.subblocks.order_by('order').first() if first_block else None
    return render(request, 'main/course_detail.html', {
        'course': course,
        'first_block': first_block,
        'first_subblock': first_subblock,
    })

def load_next_content(request, course_id, current_block_id, current_subblock_id=None):
    course = get_object_or_404(Course, id=course_id)
    current_block = get_object_or_404(Block, id=current_block_id, course=course)
    
    if current_subblock_id:
        current_subblock = get_object_or_404(SubBlock, id=current_subblock_id, block=current_block)
        next_subblock = SubBlock.objects.filter(
            block=current_block, order__gt=current_subblock.order
        ).order_by('order').first()
        
        if next_subblock:
            return render(request, 'main/partial_content.html', {
                'content': next_subblock,
                'content_type': 'subblock',
                'next_block_id': current_block.id,
                'next_subblock_id': next_subblock.id,
                'course_id': course_id,
            })
        
        next_block = Block.objects.filter(
            course=course, order__gt=current_block.order
        ).order_by('order').first()
        
        if next_block:
            return render(request, 'main/partial_content.html', {
                'content': next_block,
                'content_type': 'block',
                'next_block_id': next_block.id,
                'next_subblock_id': None,
                'course_id': course_id,
            })
    
    else:
        next_subblock = SubBlock.objects.filter(
            block=current_block
        ).order_by('order').first()
        
        if next_subblock:
            return render(request, 'main/partial_content.html', {
                'content': next_subblock,
                'content_type': 'subblock',
                'next_block_id': current_block.id,
                'next_subblock_id': next_subblock.id,
                'course_id': course_id,
            })
        
        next_block = Block.objects.filter(
            course=course, order__gt=current_block.order
        ).order_by('order').first()
        
        if next_block:
            return render(request, 'main/partial_content.html', {
                'content': next_block,
                'content_type': 'block',
                'next_block_id': next_block.id,
                'next_subblock_id': None,
                'course_id': course_id,
            })
    
    return HttpResponse('')

def load_content(request, course_id, block_id, subblock_id=None):
    course = get_object_or_404(Course, id=course_id)
    blocks = course.blocks.order_by('order')
    
    contents = []
    target_block = get_object_or_404(Block, id=block_id, course=course)
    for block in blocks:
        if block.order <= target_block.order:
            contents.append({
                'content': block,
                'content_type': 'block',
                'next_block_id': block.id,
                'next_subblock_id': None,
            })
            if block.id == block_id and subblock_id:
                subblocks = block.subblocks.order_by('order')
                target_subblock = get_object_or_404(SubBlock, id=subblock_id, block=block)
                for subblock in subblocks:
                    if subblock.order <= target_subblock.order:
                        contents.append({
                            'content': subblock,
                            'content_type': 'subblock',
                            'next_block_id': block.id,
                            'next_subblock_id': subblock.id,
                        })
    
    return render(request, 'main/partial_content_list.html', {
        'contents': contents,
        'target_id': f"{'subblock' if subblock_id else 'block'}-{subblock_id if subblock_id else block_id}",
    })