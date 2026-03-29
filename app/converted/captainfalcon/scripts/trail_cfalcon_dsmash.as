package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_dsmash extends MovieClip
    {

        public function trail_cfalcon_dsmash()
        {
            super();
            addFrameScript(10, this.frame11);
        }

        internal function frame11():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

