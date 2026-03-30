package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ZeldaKirby_307 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var reverseBox:MovieClip;
        public var self:KirbyExt;

        public function ZeldaKirby_307()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 8, this.frame9, 20, this.frame21, 35, this.frame36);
        }

        public function reflected(_arg_1:*=null):*
        {
            this.self.playSound("reflect_sfx");
            SSF2API.attachEffect("reflect_effect", {
                "x":_arg_1.data.opponent.getX(),
                "y":_arg_1.data.opponent.getY()
            });
        }

        internal function frame1():*
        {
            this.self = SSF2Utils.cast(SSF2API.getCharacter(this), KirbyExt);
            if (SSF2API.isReady())
            {
                this.self.addEventListener(SSF2Event.REVERSE_HIT, this.reflected);
            };
        }

        internal function frame2():*
        {
            this.self.setIntangibility(true);
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
        }

        internal function frame5():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame9():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame21():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":5,
                "power":45,
                "kbConstant":70,
                "direction":50,
                "effectSound":"sw_brawl_hit_M"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":5,
                "power":45,
                "kbConstant":70,
                "direction":50,
                "effectSound":"sw_brawl_hit_M"
            });
            this.self.updateAttackBoxStats(3, {
                "damage":5,
                "power":45,
                "kbConstant":70,
                "direction":50,
                "effectSound":"sw_brawl_hit_M"
            });
            this.self.refreshAttackID();
            this.self.updateAttackStats({"refreshRate":100});
        }

        internal function frame36():*
        {
            this.self.endAttack();
        }


    }
}

