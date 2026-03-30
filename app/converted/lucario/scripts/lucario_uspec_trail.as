package
{
    import flash.display.MovieClip;

    public dynamic class lucario_uspec_trail extends MovieClip
    {

        public function lucario_uspec_trail()
        {
            super();
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

