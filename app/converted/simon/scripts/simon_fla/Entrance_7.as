package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_7 extends MovieClip
    {

        public var self:SimonExt;

        public function Entrance_7()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 7, this.frame8, 29, this.frame30, 38, this.frame39, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
        }

        internal function frame2():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_simon_entrance", true);
            };
        }

        internal function frame8():*
        {
            this.self.playSound("ssf2_snd_sfx_simon_attack_swing_m");
        }

        internal function frame30():*
        {
            this.self.attachEffect("global_dust_cloud");
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("simon_land_heavy");
                };
            };
        }

        internal function frame39():*
        {
            this.self.attachEffect("dust", {
                "scaleX":1.4,
                "scaleY":1.4,
                "x":this.self.flipX(-134.5),
                "y":-153.5
            });
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }


    }
}

