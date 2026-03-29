package
{
    import flash.display.MovieClip;

    public dynamic class raptorboost_effect_trail extends MovieClip
    {

        public function raptorboost_effect_trail()
        {
            super();
            addFrameScript(14, this.frame15);
        }

        internal function frame15():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

