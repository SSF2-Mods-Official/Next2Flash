package
{
    import flash.display.MovieClip;

    public dynamic class fox_blasterEffectBack extends MovieClip
    {

        public function fox_blasterEffectBack()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

