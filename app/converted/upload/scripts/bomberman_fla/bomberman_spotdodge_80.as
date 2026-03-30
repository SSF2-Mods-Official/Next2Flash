package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_spotdodge_80 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_spotdodge_80()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame2():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

