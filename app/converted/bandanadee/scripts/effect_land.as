package
{
    import flash.display.MovieClip;

    public dynamic class effect_land extends MovieClip
    {

        public function effect_land()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

