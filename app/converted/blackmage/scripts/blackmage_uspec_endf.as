package
{
    import flash.display.MovieClip;

    public dynamic class blackmage_uspec_endf extends MovieClip
    {

        public function blackmage_uspec_endf()
        {
            super();
            addFrameScript(15, this.frame16);
        }

        internal function frame16():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

