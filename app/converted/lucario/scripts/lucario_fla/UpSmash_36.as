package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class UpSmash_36 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var xframe:String;

        public function UpSmash_36()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 47, this.frame48, 48, this.frame49, 50, this.frame51, 63, this.frame64, 68, this.frame69);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
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
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame48():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame49():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_usmash", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.75,
                "scaleY":0.6
            });
        }

        internal function frame51():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":(15 * this.self.auraMultiplier),
                "canDI":true,
                "power":62,
                "weightKB":0,
                "kbConstant":(84 - ((Math.pow((this.self.auraMultiplier + 0.33), 2) - 1) * 7)),
                "direction":82,
                "reversableAngle":false,
                "effectSound":"lucario_hit_ml",
                "hitStun":-1,
                "selfHitStun":2,
                "hitLag":-1
            });
            this.self.refreshAttackID();
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
            SSF2API.getCamera().shake(3);
        }

        internal function frame64():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame69():*
        {
            this.self.endAttack();
        }


    }
}

