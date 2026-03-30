package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_starko_103 extends MovieClip
    {

        public var self:BombermanExt;

        public function bomberman_starko_103()
        {
            super();
            addFrameScript(0, this.frame1, 84, this.frame85);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame85():*
        {
            this.self.attachEffect("effect_explosion", {
                "y":125,
                "scaleX":0.6,
                "scaleY":0.6,
                "parentLock":false,
                "behind":true
            });
        }


    }
}

