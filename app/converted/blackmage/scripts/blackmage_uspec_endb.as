package
{
    import flash.display.MovieClip;

    public dynamic class blackmage_uspec_endb extends MovieClip
    {

        public function blackmage_uspec_endb()
        {
            super();
            addFrameScript(11, this.frame12);
        }

        internal function frame12():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

