package
{
    import flash.display.MovieClip;

    public dynamic class trail_cfalcon_fsmash extends MovieClip
    {

        public function trail_cfalcon_fsmash()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

