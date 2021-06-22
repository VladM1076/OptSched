//  (VLAD) Created my own class to replace SmallPtrSet/SmallSet
//  since SmallPtrSet/SmallSet is not supported on device

template <typename T>
class DeviceSet {
  public:
    __host__ __device__
    DeviceSet(int size = 0) {
      size_ = size;
      alloc_ = size;

      if (alloc_ > 0)
        elmnt = new T[alloc_];
      else
        elmnt = NULL;
    }
    __host__ __device__
    ~DeviceSet() {
      if (elmnt)
        delete[] elmnt;
    }
    
    //inserts entry into set, returns true if
    //entry is a duplicate
    __host__ __device__
    bool insert(T entry) {
      bool insert = true;
      if (alloc_ == 0) {
	alloc_ = 4;
        elmnt = new T[alloc_];
	elmnt[size_++] = entry;
      } else {
        //check if entry has already been entered
        for (int i = 0; i < size_; i++) {
          if (entry == elmnt[i])
            insert = false;
        }
	//if not duplicate, insert
	if (insert) {
	  //allocate more space if full
	  if (alloc_ == size_) {
	    alloc_ *= 2;
	    T *new_arr = new T[alloc_];
	    //copy old array
	    for (int i = 0; i < size_; i++)
	      new_arr[i] = elmnt[i];
	    delete[] elmnt;
	    elmnt = new_arr;
	  }
	  //add entry to array
          elmnt[size_++] = entry;
	}
      }
      return insert;
    }

    __host__ __device__
    int size() const {
      return size_;
    }

    //searches set for entry, returns true if match is found
    __host__ __device__
    bool contains(T entry) const {
      for (int i = 0; i < size_; i++) {
        if (elmnt[i] == entry)
          return true;
      }
      return false;
    }

    // searches for entry, erases it from array and returns true if found
    __host__ __device__
    bool erase (T entry) {
      bool erased = false;
      for (int i = 0; i < size_; i++) {
        if (erased)
          elmnt[i] = elmnt[i + 1];
        if (!erased && elmnt[i] == entry) {
          if (i < size_ - 1)
            elmnt[i] = elmnt[i + 1];
          size_--;
          erased = true;
        }
      }
      return erased;
    }

    __host__ __device__
    T& operator[](int indx) {
      if (indx < size_ && indx >= 0)
        return elmnt[indx];
      else {
        printf("Index out of bounds!\n");
	return NULL;
      }
    }

    __host__ __device__
    void Reset() {
      size_ = 0;
    }

    // Iterator Class
    class iterator {
    private:
        // Dynamic array using pointers
        T *ptr;

    public:
        __host__ __device__
        explicit iterator()
            : ptr(nullptr)
        {
        }
        __host__ __device__
        explicit iterator(T *p)
            : ptr(p)
        {
        }
        __host__ __device__
        bool operator==(const iterator& rhs) const
        {
            return ptr == rhs.ptr;
        }
        __host__ __device__
        bool operator!=(const iterator& rhs) const
        {
            return !(*this == rhs);
        }
        __host__ __device__
        T operator*() const
        {
            return *ptr;
        }
        __host__ __device__
        iterator& operator++()
        {
            ++ptr;
            return *this;
        }
        __host__ __device__
        iterator operator++(int)
        {
            iterator temp(*this);
            ++*this;
            return temp;
        }
    };

    // Begin iterator
    __host__ __device__
    iterator begin() const {
      return iterator(elmnt);
    }

    // End iterator
    __host__ __device__
    iterator end() const {
      return iterator(elmnt + size_);
    }

    int size_;
    int alloc_;
    T *elmnt;
};
