package
{
    import flash.display.MovieClip;

    public dynamic class kirby_powerstar extends MovieClip
    {

        public function kirby_powerstar()
        {
            super();
            addFrameScript(0, this.frame1, 21, this.frame22);
        }

        internal function frame1():*
        {
            SSF2API.playSound("ssf2_snd_sfx_kirby_abilityLoss");
        }

        internal function frame22():*
        {
            stop();
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

