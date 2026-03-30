package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_70 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var effect:*;

        public function DodgeRoll_70()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 12, this.frame13, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame9():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame13():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("simon_land_heavy");
                };
            };
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

