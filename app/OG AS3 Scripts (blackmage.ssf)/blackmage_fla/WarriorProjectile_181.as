// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.WarriorProjectile_181

package blackmage_fla
{
    import flash.display.MovieClip;
    import flash.geom.*;
    import flash.display.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class WarriorProjectile_181 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var self:*;
        public var jumpedToSwing:Boolean;
        public var oldX:Number;
        public var stuckCount:Number;
        public var character:*;
        public var temp:*;

        public function WarriorProjectile_181()
        {
            addFrameScript(0, this.frame1, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 20, this.frame21, 21, this.frame22, 23, this.frame24, 26, this.frame27, 38, this.frame39, 42, this.frame43, 43, this.frame44, 52, this.frame53);
        }

        public function jumpToSwing():*
        {
            if (!this.jumpedToSwing)
            {
                this.jumpedToSwing = true;
                this.self.stancePlayFrame("attack");
                this.self.destroyTimer(this.checkActivation);
                this.self.destroyTimer(this.checkStuck);
            };
        }

        public function onHit(_arg_1:*=null):*
        {
            if (((_arg_1.data.receiver.isDisposed()) || (!(_arg_1.data.receiver.getType() === "SSF2Character"))))
            {
                return;
            };
            _arg_1.data.receiver.grab(this.character.getUID(), true, false, true);
            this.temp = this.character.getGlobalVariable("fsTargets");
            this.temp.push(_arg_1.data.receiver);
            this.character.setGlobalVariable("fsTargets", this.temp);
            SSF2API.getCamera().shake(12);
            this.jumpToSwing();
        }

        public function checkActivation():*
        {
            this.temp = this.character.getGlobalVariable("fsTargets");
            if (this.temp.length > 0)
            {
                this.jumpToSwing();
            };
        }

        public function checkStuck():*
        {
            if (this.oldX === this.self.getX())
            {
                this.stuckCount++;
                if (this.stuckCount > 5)
                {
                    this.jumpToSwing();
                };
            }
            else
            {
                this.stuckCount = 0;
            };
            this.oldX = this.self.getX();
        }

        public function land(_arg_1:*=null):*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.attachEffect("effect_land");
            this.self.stancePlayFrame("land");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.land);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.jumpedToSwing = false;
            this.oldX = 0;
            this.stuckCount = 0;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.updateAttackStats({"air_ease":0});
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
                this.self.createTimer(1, 0, this.checkActivation);
            };
        }

        internal function frame10():*
        {
            this.self.setXSpeed(4, false);
            this.self.createTimer(1, 0, this.checkStuck);
        }

        internal function frame11():*
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame12():*
        {
            this.self.setXSpeed(13, false);
        }

        internal function frame13():*
        {
            this.self.setXSpeed(18, false);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame14():*
        {
            this.self.setXSpeed(28, false);
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame22():*
        {
            this.self.setXSpeed(18, false);
        }

        internal function frame24():*
        {
            this.self.setXSpeed(5, false);
        }

        internal function frame27():*
        {
            this.self.setXSpeed(0);
        }

        internal function frame39():*
        {
            this.self.setXSpeed(-5, false);
            this.self.setYSpeed(-10);
            this.self.updateProjectileStats({
                "gravity":1.5,
                "maxgravity":12
            });
            this.self.updateAttackStats({"air_ease":-1});
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.land);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("landwait");
        }

        internal function frame44():*
        {
            this.self.attachEffect("bm_fs_warp");
            this.self.playSound("bm_Warp_part2");
        }

        internal function frame53():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

