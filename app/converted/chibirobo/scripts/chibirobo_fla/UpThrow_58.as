package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class UpThrow_58 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var touchBox:MovieClip;
        public var self:ChibiExt;

        public function UpThrow_58()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 7, this.frame8, 11, this.frame12, 14, this.frame15, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (this.self && SSF2API.isReady())
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
            };
        }

        internal function frame6():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame8():*
        {
            this.self.attachEffect("chibi_uthrowEffect");
        }

        internal function frame12():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.updateAttackBoxStats(2, {
                "hasEffect":true,
                "damage":4,
                "power":60,
                "kbConstant":50,
                "hitStun":2,
                "selfHitStun":1,
                "effectSound":"sfx_waterhit_m",
                "effect_id":"effect_waterhit_heavy"
            });
            this.self.updateAttackStats({"refreshRate":30});
            this.self.refreshAttackID();
            this.self.attachEffectOverlay("bubbleExplosion", {"y":-100});
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

