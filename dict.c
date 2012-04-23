#include <stdlib.h>
#include <stddef.h>
#include <assert.h>
#include "dict.h"

/*
 * These macros provide short convenient names for structure members,
 * which are embellished with dict_ prefixes so that they are
 * properly confined to the documented namespace. It's legal for a 
 * program which uses dict to define, for instance, a macro called ``parent''.
 * Such a macro would interfere with the dnode_t struct definition.
 * In general, highly portable and reusable C modules which expose their
 * structures need to confine structure member names to well-defined spaces.
 * The resulting identifiers aren't necessarily convenient to use, nor
 * readable, in the implementation, however!
 */

#define left dict_left
#define right dict_right
#define parent dict_parent
#define color dict_color
#define key dict_key
#define data dict_data

#define nilnode dict_nilnode
#define nodecount dict_nodecount
#define maxcount dict_maxcount
#define compare dict_compare
#define allocnode dict_allocnode
#define freenode dict_freenode

#define dictptr dict_dictptr

#define dict_root(D) ((D)->nilnode.left)
#define dict_nil(D) (&(D)->nilnode)
#define DICT_DEPTH_MAX 64

/*
 * Perform a ``left rotation'' adjustment on the tree.  The given node P and
 * its right child C are rearranged so that the P instead becomes the left
 * child of C.   The left subtree of C is inherited as the new right subtree
 * for P.  The ordering of the keys within the tree is thus preserved.
 */

static void attach_child_right(dnode_t *parent_node, dnode_t *child_node)
{
    parent_node->right = child_node;
    child_node->parent = parent_node;
}

static void attach_child_left(dnode_t *parent_node, dnode_t *child_node)
{
    parent_node->left = child_node;
    child_node->parent = parent_node;
}

static void rotate_left(dnode_t *upper)
{
    dnode_t *lower, *lowleft, *grandparent;

    lower = upper->right;
    lowleft = lower->left;
    grandparent = upper->parent;

    attach_child_right(upper, lowleft);

    if (upper == grandparent->left) {
        attach_child_left(grandparent, lower);
    } else if (upper == grandparent->right){
        attach_child_right(grandparent, lower);
    } else {
        assert(0);
    }

    attach_child_left(lower, upper);
}

static void rotate_right(dnode_t *upper)
{
    dnode_t *lower, *lowright, *grandparent;

    lower = upper->left;
    lowright = lower->right;
    grandparent = upper->parent;

    attach_child_left(upper, lowright);

    if (upper == grandparent->right) {
        attach_child_right(grandparent, lower);
    } else if (upper == grandparent->left) {
        attach_child_left(grandparent, lower);
    } else {
        assert(0);
    }

    attach_child_right(lower, upper);
}

static int verify_bintree(dict_t *dict)
{
    dnode_t *first, *next;

    first = dict_first(dict);

	while (first && (next = dict_next(dict, first))) {
	    if (dict->compare(first->key, next->key) >= 0)
		return 0;
	    first = next;
	}
    return 1;
}


/*
 * This function recursively verifies that the given binary subtree satisfies
 * three of the red black properties. It checks that every red node has only
 * black children. It makes sure that each node is either red or black. And it
 * checks that every path has the same count of black nodes from root to leaf.
 * It returns the blackheight of the given subtree; this allows blackheights to
 * be computed recursively and compared for left and right siblings for
 * mismatches. It does not check for every nil node being black, because there
 * is only one sentinel nil node. The return value of this function is the
 * black height of the subtree rooted at the node ``root'', or zero if the
 * subtree is not red-black.
 */

static unsigned int verify_redblack(dnode_t *nil, dnode_t *root)
{
    unsigned height_left, height_right;

    if (root != nil) {
	height_left = verify_redblack(nil, root->left);
	height_right = verify_redblack(nil, root->right);
	if (height_left == 0 || height_right == 0)
	    return 0;
	if (height_left != height_right)
	    return 0;
	if (root->color == dnode_red) {
	    if (root->left->color != dnode_black)
		return 0;
	    if (root->right->color != dnode_black)
		return 0;
	    return height_left;
	}
	if (root->color != dnode_black)
	    return 0;
	return height_left + 1;
    } 
    return 1;
}

static dictcount_t verify_node_count(dnode_t *nil, dnode_t *root)
{
    if (root == nil)
	return 0;
    else
	return 1 + verify_node_count(nil, root->left)
	    + verify_node_count(nil, root->right);
}


dict_t *dict_init(dict_t *dict, dictcount_t maxcount, dict_comp_t comp)
{
    dict->compare = comp;
    dict->nodecount = 0;
    dict->maxcount = maxcount;
    dict->nilnode.left = &dict->nilnode;
    dict->nilnode.right = &dict->nilnode;
    dict->nilnode.parent = &dict->nilnode;
    dict->nilnode.color = dnode_black;
    return dict;
}

/*
 * Verify the integrity of the dictionary structure.  This is provided for
 * debugging purposes, and should be placed in assert statements.   Just because
 * this function succeeds doesn't mean that the tree is not corrupt. Certain
 * corruptions in the tree may simply cause undefined behavior.
 */ 

int dict_verify(dict_t *dict)
{
    dnode_t *nil = dict_nil(dict), *root = dict_root(dict);

    /* check that the sentinel node and root node are black */
    if (root->color != dnode_black)
	return 0;
    if (nil->color != dnode_black)
	return 0;
    if (nil->right != nil)
	return 0;
    /* nil->left is the root node; check that its parent pointer is nil */
    if (nil->left->parent != nil)
	return 0;
    /* perform a weak test that the tree is a binary search tree */
    if (!verify_bintree(dict))
	return 0;
    /* verify that the tree is a red-black tree */
    if (!verify_redblack(nil, root))
	return 0;
    if (verify_node_count(nil, root) != dict_count(dict))
	return 0;
    return 1;
}

/*
 * Locate a node in the dictionary having the given key.
 * If the node is not found, a null a pointer is returned (rather than 
 * a pointer that dictionary's nil sentinel node), otherwise a pointer to the
 * located node is returned.
 */

dnode_t *dict_lookup(dict_t *dict, const void *key)
{
    dnode_t *root = dict_root(dict);
    dnode_t *nil = dict_nil(dict);
    int result;

    /* simple binary search adapted for trees that contain duplicate keys */

    while (root != nil) {
	    result = dict->compare(key, root->key);
	    if (result < 0)
	        root = root->left;
	    else if (result > 0)
	        root = root->right;
	    else {
	    	return root;
	    }
    }

    return NULL;
}

/*
 * Insert a node into the dictionary. The node should have been
 * initialized with a data field. All other fields are ignored.
 * The behavior is undefined if the user attempts to insert into
 * a dictionary that is already full (for which the dict_isfull()
 * function returns true).
 */

void dict_insert(dict_t *dict, dnode_t *node, const void *key)
{
    dnode_t *where = dict_root(dict), *nil = dict_nil(dict);
    dnode_t *parent = nil, *uncle, *grandpa;
    int result = -1;

    node->key = key;

    assert (!dict_isfull(dict));
    assert (!dict_contains(dict, node));

    /* basic binary tree insert */

    while (where != nil) {
	    parent = where;
	    result = dict->compare(key, where->key);
	    if (result < 0)
	        where = where->left;
	    else
	        where = where->right;
    }

    assert (where == nil);

    if (result < 0)
	parent->left = node;
    else
	parent->right = node;

    node->parent = parent;
    node->left = nil;
    node->right = nil;

    dict->nodecount++;

    /* red black adjustments */

    node->color = dnode_red;

    while (parent->color == dnode_red) {
	    grandpa = parent->parent;
	    if (parent == grandpa->left) {
	        uncle = grandpa->right;
	        if (uncle->color == dnode_red) {	/* red parent, red uncle */
	    	parent->color = dnode_black;
	    	uncle->color = dnode_black;
	    	grandpa->color = dnode_red;
	    	node = grandpa;
	    	parent = grandpa->parent;
	        } else {				/* red parent, black uncle */
	        	if (node == parent->right) {
	    	    rotate_left(parent);
	    	    parent = node;
	    	    assert (grandpa == parent->parent);
	    	    /* rotation between parent and child preserves grandpa */
	    	}
	    	parent->color = dnode_black;
	    	grandpa->color = dnode_red;
	    	rotate_right(grandpa);
	    	break;
	        }
	    } else { 	/* symmetric cases: parent == parent->parent->right */
	        uncle = grandpa->left;
	        if (uncle->color == dnode_red) {
	    	parent->color = dnode_black;
	    	uncle->color = dnode_black;
	    	grandpa->color = dnode_red;
	    	node = grandpa;
	    	parent = grandpa->parent;
	        } else {
	        	if (node == parent->left) {
	    	    rotate_right(parent);
	    	    parent = node;
	    	    assert (grandpa == parent->parent);
	    	}
	    	parent->color = dnode_black;
	    	grandpa->color = dnode_red;
	    	rotate_left(grandpa);
	    	break;
	        }
	    }
    }

    dict_root(dict)->color = dnode_black;

    assert (dict_verify(dict));
}

/*
 * Delete the given node from the dictionary. If the given node does not belong
 * to the given dictionary, undefined behavior results.  A pointer to the
 * deleted node is returned.
 */

dnode_t *dict_delete(dict_t *dict, dnode_t *delete)
{
    dnode_t *nil = dict_nil(dict), *child, *delparent = delete->parent;

    /* basic deletion */

    assert (dict_contains(dict, delete));

    /*
     * If the node being deleted has two children, then we replace it with its
     * successor (i.e. the leftmost node in the right subtree.) By doing this,
     * we avoid the traditional algorithm under which the successor's key and
     * value *only* move to the deleted node and the successor is spliced out
     * from the tree. We cannot use this approach because the user may hold
     * pointers to the successor, or nodes may be inextricably tied to some
     * other structures by way of embedding, etc. So we must splice out the
     * node we are given, not some other node, and must not move contents from
     * one node to another behind the user's back.
     */

    if (delete->left != nil && delete->right != nil) {
	dnode_t *next = dict_next(dict, delete);
	dnode_t *nextparent = next->parent;
	dnode_color_t nextcolor = next->color;

	assert (next != nil);
	assert (next->parent != nil);
	assert (next->left == nil);

	/*
	 * First, splice out the successor from the tree completely, by
	 * moving up its right child into its place.
	 */

	child = next->right;
	child->parent = nextparent;

	if (nextparent->left == next) {
	    nextparent->left = child;
	} else {
	    assert (nextparent->right == next);
	    nextparent->right = child;
	}

	/*
	 * Now that the successor has been extricated from the tree, install it
	 * in place of the node that we want deleted.
	 */

	next->parent = delparent;
	next->left = delete->left;
	next->right = delete->right;
	next->left->parent = next;
	next->right->parent = next;
	next->color = delete->color;
	delete->color = nextcolor;

	if (delparent->left == delete) {
	    delparent->left = next;
	} else {
	    assert (delparent->right == delete);
	    delparent->right = next;
	}

    } else {
	assert (delete != nil);
	assert (delete->left == nil || delete->right == nil);

	child = (delete->left != nil) ? delete->left : delete->right;

	child->parent = delparent = delete->parent;	    

	if (delete == delparent->left) {
	    delparent->left = child;    
	} else {
	    assert (delete == delparent->right);
	    delparent->right = child;
	}
    }

    delete->parent = NULL;
    delete->right = NULL;
    delete->left = NULL;

    dict->nodecount--;

    assert (verify_bintree(dict));

    /* red-black adjustments */

    if (delete->color == dnode_black) {
	dnode_t *parent, *sister;

	dict_root(dict)->color = dnode_red;

	while (child->color == dnode_black) {
	    parent = child->parent;
	    if (child == parent->left) {
		sister = parent->right;
		assert (sister != nil);
		if (sister->color == dnode_red) {
		    sister->color = dnode_black;
		    parent->color = dnode_red;
		    rotate_left(parent);
		    sister = parent->right;
		    assert (sister != nil);
		}
		if (sister->left->color == dnode_black
			&& sister->right->color == dnode_black) {
		    sister->color = dnode_red;
		    child = parent;
		} else {
		    if (sister->right->color == dnode_black) {
			assert (sister->left->color == dnode_red);
			sister->left->color = dnode_black;
			sister->color = dnode_red;
			rotate_right(sister);
			sister = parent->right;
			assert (sister != nil);
		    }
		    sister->color = parent->color;
		    sister->right->color = dnode_black;
		    parent->color = dnode_black;
		    rotate_left(parent);
		    break;
		}
	    } else {	/* symmetric case: child == child->parent->right */
		assert (child == parent->right);
		sister = parent->left;
		assert (sister != nil);
		if (sister->color == dnode_red) {
		    sister->color = dnode_black;
		    parent->color = dnode_red;
		    rotate_right(parent);
		    sister = parent->left;
		    assert (sister != nil);
		}
		if (sister->right->color == dnode_black
			&& sister->left->color == dnode_black) {
		    sister->color = dnode_red;
		    child = parent;
		} else {
		    if (sister->left->color == dnode_black) {
			assert (sister->right->color == dnode_red);
			sister->right->color = dnode_black;
			sister->color = dnode_red;
			rotate_left(sister);
			sister = parent->left;
			assert (sister != nil);
		    }
		    sister->color = parent->color;
		    sister->left->color = dnode_black;
		    parent->color = dnode_black;
		    rotate_right(parent);
		    break;
		}
	    }
	}

	child->color = dnode_black;
	dict_root(dict)->color = dnode_black;
    }

    assert (dict_verify(dict));

    return delete;
}

/*
 * Return the node with the lowest (leftmost) key. If the dictionary is empty
 * (that is, dict_isempty(dict) returns 1) a null pointer is returned.
 */

dnode_t *dict_first(dict_t *dict)
{
    dnode_t *nil = dict_nil(dict), *root = dict_root(dict), *left;

    if (root != nil)
	while ((left = root->left) != nil)
	    root = left;

    return (root == nil) ? NULL : root;
}

/*
 * Return the node with the highest (rightmost) key. If the dictionary is empty
 * (that is, dict_isempty(dict) returns 1) a null pointer is returned.
 */

dnode_t *dict_last(dict_t *dict)
{
    dnode_t *nil = dict_nil(dict), *root = dict_root(dict), *right;

    if (root != nil)
	while ((right = root->right) != nil)
	    root = right;

    return (root == nil) ? NULL : root;
}

/*
 * Return the given node's successor node---the node which has the
 * next key in the the left to right ordering. If the node has
 * no successor, a null pointer is returned rather than a pointer to
 * the nil node.
 */

dnode_t *dict_next(dict_t *dict, dnode_t *curr)
{
    dnode_t *nil = dict_nil(dict), *parent, *left;

    if (curr->right != nil) {
	curr = curr->right;
	while ((left = curr->left) != nil)
	    curr = left;
	return curr;
    }

    parent = curr->parent;

    while (parent != nil && curr == parent->right) {
	curr = parent;
	parent = curr->parent;
    }

    return (parent == nil) ? NULL : parent;
}

/*
 * Return the given node's predecessor, in the key order.
 * The nil sentinel node is returned if there is no predecessor.
 */

dnode_t *dict_prev(dict_t *dict, dnode_t *curr)
{
    dnode_t *nil = dict_nil(dict), *parent, *right;

    if (curr->left != nil) {
	curr = curr->left;
	while ((right = curr->right) != nil)
	    curr = right;
	return curr;
    }

    parent = curr->parent;

    while (parent != nil && curr == parent->left) {
	curr = parent;
	parent = curr->parent;
    }

    return (parent == nil) ? NULL : parent;
}


#undef dict_count
#undef dict_isfull
#undef dnode_get
#undef dnode_put
#undef dnode_getkey

dictcount_t dict_count(dict_t *dict)
{
    return dict->nodecount;
}

int dict_isfull(dict_t *dict)
{
    return dict->nodecount == dict->maxcount;
}

dnode_t *dnode_init(dnode_t *dnode, void *data, int type, int length)
{
    dnode->data = data;
    dnode->type = type;
    dnode->length = length;
    dnode->parent = NULL;
    dnode->left = NULL;
    dnode->right = NULL;
    return dnode;
}

void *dnode_get(dnode_t *dnode, int *type, int *length)
{
    *type = dnode->type;
    *length = dnode->length;
    return dnode->data;
}

const void *dnode_getkey(dnode_t *dnode)
{
    return dnode->key;
}

void dnode_put(dnode_t *dnode, void *data, int type, int length)
{
    dnode->data = data;
    dnode->type = type;
    dnode->length = length;
}
