package
{
    import flash.display.MovieClip;

    public dynamic class fs_hit extends MovieClip
    {

        public function fs_hit()
        {
            super();
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

