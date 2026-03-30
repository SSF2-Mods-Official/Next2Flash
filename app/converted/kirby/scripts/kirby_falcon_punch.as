package
{
    import flash.display.MovieClip;

    public dynamic class kirby_falcon_punch extends MovieClip
    {

        public function kirby_falcon_punch()
        {
            super();
            addFrameScript(36, this.frame37);
        }

        internal function frame37():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

