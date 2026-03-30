package
{
    import flash.display.MovieClip;

    public dynamic class dee_fs_star_trail extends MovieClip
    {

        public function dee_fs_star_trail()
        {
            super();
            addFrameScript(16, this.frame17);
        }

        internal function frame17():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

