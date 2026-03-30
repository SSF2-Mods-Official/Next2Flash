package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_dash extends MovieClip
    {

        public function trail_lucario_dash()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

