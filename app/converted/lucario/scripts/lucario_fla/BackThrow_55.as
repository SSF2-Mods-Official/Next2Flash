package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class BackThrow_55 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:LucarioExt;

        public function BackThrow_55()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 8, this.frame9, 10, this.frame11, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame8():*
        {
            this.self.attachEffect("global_dust_cloud", {
                "x":this.self.flipX(25),
                "scaleX":0.75,
                "scaleY":0.75
            });
            this.self.attachEffect("ground_bounce", {
                "x":this.self.flipX(25),
                "scaleX":0.75,
                "scaleY":0.75
            });
        }

        internal function frame9():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame11():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

