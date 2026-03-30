package
{
    import flash.display.MovieClip;

    public dynamic class dee_fs_sparkle extends MovieClip
    {

        public function dee_fs_sparkle()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

