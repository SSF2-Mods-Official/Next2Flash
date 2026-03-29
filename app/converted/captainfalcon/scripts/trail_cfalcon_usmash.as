package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_usmash extends MovieClip
    {

        public function trail_cfalcon_usmash()
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

