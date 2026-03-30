package
{
    import flash.display.MovieClip;

    public dynamic class chibirobo_effect_lidopen extends MovieClip
    {

        public function chibirobo_effect_lidopen()
        {
            super();
            addFrameScript(11, this.frame12);
        }

        internal function frame12():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

