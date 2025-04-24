from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from .models import FoundItem, ClaimRequest
from .forms import FoundItemForm, ClaimRequestForm

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_claims(request):
    """Admin view for managing pending claims"""
    claims = ClaimRequest.objects.filter(status='PENDING').select_related('item', 'claimant')
    return render(request, 'found/manage_claims.html', {'claims': claims})

@login_required
@user_passes_test(lambda u: u.is_staff)
def process_claim(request, pk):
    """Admin view to process individual claims"""
    claim = get_object_or_404(ClaimRequest, pk=pk)
    
    if request.method == 'POST':
        decision = request.POST.get('decision')
        if decision == 'approve':
            claim.status = 'APPROVED'
            claim.item.status = 'CLAIMED'
            # Send approval notification
            send_mail(
                'Claim Approved - Discourse',
                f'Your claim for "{claim.item.title}" has been approved.\n\n'
                'Please contact us to arrange pickup.',
                'noreply@discourse.com',
                [claim.claimant.email],
                fail_silently=True,
            )
        else:
            claim.status = 'REJECTED'
            claim.item.status = 'FOUND'
            # Send rejection notification
            send_mail(
                'Claim Rejected - Discourse',
                f'Your claim for "{claim.item.title}" was rejected.\n\n'
                'Reason: Documentation verification failed',
                'noreply@discourse.com',
                [claim.claimant.email],
                fail_silently=True,
            )
        claim.save()
        claim.item.save()
        messages.success(request, f'Claim {claim.get_status_display()}')
        return redirect('found:manage_claims')
        
    return render(request, 'found/process_claim.html', {
        'claim': claim,
        'document_url': claim.verification_doc.url if claim.verification_doc else None
    })

@login_required
def report_found_item(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()
            messages.success(request, 'Item reported successfully!')
            return redirect('found_items')
    else:
        form = FoundItemForm()
    return render(request, 'found/report.html', {'form': form})

@login_required
def found_items(request):
    items = FoundItem.objects.filter(status='FOUND')
    return render(request, 'found/list.html', {'items': items})

@login_required
def claim_item(request, pk):
    item = get_object_or_404(FoundItem, pk=pk)
    if request.method == 'POST':
        form = ClaimRequestForm(request.POST, request.FILES)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimant = request.user
            claim.save()
            item.status = 'PENDING'
            item.save()
            messages.success(request, 'Claim request submitted for admin approval')
            return redirect('found_items')
    else:
        form = ClaimRequestForm()
    return render(request, 'found/claim.html', {'form': form, 'item': item})

@login_required
def my_claims(request):
    claims = ClaimRequest.objects.filter(claimant=request.user)
    return render(request, 'found/my_claims.html', {'claims': claims})